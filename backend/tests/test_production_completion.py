"""Real SQLite + real HTTP authentication tests; only external providers mocked."""
import hashlib
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
import pytest
from sqlalchemy import select, text
from test_auth_and_scoping import async_test_db, app_with_db, client
from backend.app.db.models import User, SocialAccount, OAuthAttempt, Post, PostPublication, Schedule, Comment, ContentTypeEnum, PostStatusEnum
from backend.app.services.session_service import digest
from backend.app.services.scheduling_service import SchedulingService


def register(client, email='owner@example.com', verified=True):
    response=client.post('/api/v1/auth/register',json={'email':email,'password':'Test-password-2984!', 'accept_terms':True})
    assert response.status_code==201, response.text
    data=response.json(); headers={'Authorization':'Bearer '+data['access_token']}
    if verified:
        assert client.post('/api/v1/auth/verify-email',json={'token':data['verification_token']},headers=headers).status_code==200
    return data,headers


def test_refresh_rotation_is_single_use_and_logout_revokes_session(client):
    data,headers=register(client)
    first=client.post('/api/v1/auth/refresh',json={'refresh_token':data['refresh_token']})
    assert first.status_code==200
    assert client.post('/api/v1/auth/refresh',json={'refresh_token':data['refresh_token']}).status_code==401
    rotated=first.json()
    assert client.post('/api/v1/auth/logout',headers=headers,json={}).status_code==200
    assert client.get('/api/v1/auth/me',headers={'Authorization':'Bearer '+rotated['access_token']}).status_code==401
    assert client.post('/api/v1/auth/refresh',json={'refresh_token':rotated['refresh_token']}).status_code==401


def test_unverified_users_cannot_bypass_ui(client):
    _,headers=register(client,verified=False)
    for route in ['/accounts','/posts','/analytics/dashboard','/models/registry','/comments']:
        assert client.get('/api/v1'+route,headers=headers).status_code==403


def test_new_workspace_is_genuinely_empty(client):
    _,headers=register(client)
    assert client.get('/api/v1/accounts',headers=headers).json()['accounts']==[]
    assert client.get('/api/v1/posts',headers=headers).json()['posts']==[]
    assert client.get('/api/v1/comments',headers=headers).json()['comments']==[]
    overview=client.get('/api/v1/analytics/dashboard',headers=headers)
    assert overview.status_code==200,overview.text
    assert overview.json()['total_connected_platforms']==0
    assert overview.json()['total_reach']==0
    assert client.get('/api/v1/analytics/comparison',headers=headers).json()['platforms']==[]
    sentiment=client.get('/api/v1/analytics/sentiment-trends',headers=headers).json()
    assert sentiment['positive_comments_count']==sentiment['neutral_comments_count']==sentiment['negative_comments_count']==0
    temporal=client.get('/api/v1/analytics/temporal',headers=headers).json()
    assert temporal['best_overall_hour'] is None and all(s['sample_posts']==0 for s in temporal['heatmap_slots'])


def test_publish_without_owned_account_is_rejected(client):
    _,headers=register(client)
    response=client.post('/api/v1/content/publish-multi',headers=headers,json={'platforms':['x'],'text':'Unsent test','publish_now':True})
    assert response.status_code==409
    assert client.get('/api/v1/posts',headers=headers).json()['total']==0


def test_profile_and_password_change_are_persistent(client):
    data,headers=register(client)
    assert client.patch('/api/v1/auth/me',headers=headers,json={'full_name':'Updated Name'}).status_code==200
    assert client.get('/api/v1/auth/me',headers=headers).json()['full_name']=='Updated Name'
    assert client.post('/api/v1/auth/password',headers=headers,json={'current_password':'wrong','password':'Replacement-123!'}).status_code==400
    assert client.post('/api/v1/auth/password',headers=headers,json={'current_password':'Test-password-2984!','password':'Replacement-123!'}).status_code==200
    assert client.get('/api/v1/auth/me',headers=headers).status_code==401
    assert client.post('/api/v1/auth/login',json={'email':'owner@example.com','password':'Replacement-123!'}).status_code==200


@pytest.mark.asyncio
async def test_credentials_are_encrypted_in_database(client,async_test_db):
    data,headers=register(client)
    setup=client.post('/api/v1/auth/2fa/setup',headers=headers)
    assert setup.status_code==200
    raw=(await async_test_db.execute(text('SELECT two_factor_secret FROM users'))).scalar_one()
    assert raw.startswith('v2$') and raw!=setup.json()['secret']
    account=SocialAccount(user_id=UUID(data['user']['id']),platform='x',platform_user_id='a1',access_token='test-provider-token',refresh_token='test-provider-refresh')
    async_test_db.add(account);await async_test_db.commit()
    row=(await async_test_db.execute(text('SELECT access_token, refresh_token FROM social_accounts'))).one()
    assert all(value.startswith('v2$') for value in row)


@pytest.mark.asyncio
async def test_password_reset_single_use_and_no_user_enumeration(client,async_test_db):
    _,headers=register(client)
    known=client.post('/api/v1/auth/forgot-password',json={'email':'owner@example.com'})
    unknown=client.post('/api/v1/auth/forgot-password',json={'email':'absent@example.com'})
    assert known.json()==unknown.json()
    user=await async_test_db.scalar(select(User))
    user.password_reset_hash=digest('test-reset-token')
    user.password_reset_expiry=datetime.now(timezone.utc).replace(tzinfo=None)+timedelta(minutes=10)
    await async_test_db.commit()
    payload={'token':'test-reset-token','password':'New-passphrase-485!'}
    assert client.post('/api/v1/auth/reset-password',json=payload).status_code==200
    assert client.post('/api/v1/auth/reset-password',json=payload).status_code==400
    assert client.get('/api/v1/auth/me',headers=headers).status_code==401


@pytest.mark.asyncio
async def test_oauth_rejects_cross_user_state_and_replay(client,async_test_db):
    first,h1=register(client)
    second,h2=register(client,'second@example.com')
    expiry=datetime.now(timezone.utc).replace(tzinfo=None)+timedelta(minutes=10)
    async_test_db.add(OAuthAttempt(state_hash=digest('state-test'),user_id=UUID(first['user']['id']),platform='x',redirect_uri='http://localhost:3000/oauth/callback',expires_at=expiry,consumed=False))
    await async_test_db.commit()
    payload={'platform':'x','state':'state-test','code':'test-code','redirect_uri':'http://localhost:3000/oauth/callback'}
    assert client.post('/api/v1/auth/oauth/callback',headers=h2,json=payload).status_code==400
    adapter=MagicMock();adapter.auth.exchange_code=AsyncMock(return_value={'access_token':'provider-secret','scope':'read write'})
    adapter.auth.get_user_profile=AsyncMock(return_value={'id':'provider-account','username':'provider-user'})
    with patch('backend.app.services.oauth_service.configured_adapter',return_value=adapter):
        result=client.post('/api/v1/auth/oauth/callback',headers=h1,json=payload)
        assert result.status_code==200,result.text
        assert 'provider-secret' not in result.text
        assert client.post('/api/v1/auth/oauth/callback',headers=h1,json=payload).status_code==400


@pytest.mark.asyncio
async def test_inbox_and_comment_actions_are_tenant_scoped(client,async_test_db):
    first,h1=register(client);_,h2=register(client,'second@example.com')
    post=Post(user_id=UUID(first['user']['id']),content_type=ContentTypeEnum.POST,status=PostStatusEnum.PUBLISHED)
    async_test_db.add(post);await async_test_db.flush()
    comment=Comment(post_id=post.id,platform='x',platform_comment_id='provider-comment',text='Owner-only comment')
    async_test_db.add(comment);await async_test_db.commit()
    assert len(client.get('/api/v1/comments',headers=h1).json()['comments'])==1
    assert client.get('/api/v1/comments',headers=h2).json()['comments']==[]
    for method,path,body in [('POST',f'/comments/x/{comment.id}/reply',{'text':'Denied'}),('DELETE',f'/comments/x/{comment.id}',None),('POST',f'/comments/x/{comment.id}/hide',{})]:
        response=client.request(method,'/api/v1'+path,headers=h2,json=body)
        assert response.status_code==404


@pytest.mark.asyncio
async def test_schedule_is_local_and_dispatch_claim_is_single_use(client,async_test_db):
    data,headers=register(client)
    async_test_db.add(SocialAccount(user_id=UUID(data['user']['id']),platform='x',platform_user_id='test-user',access_token='test-provider-token'))
    await async_test_db.commit()
    adapter=MagicMock();adapter.publish_post=AsyncMock(return_value=MagicMock(status='published',platform_post_id='test-post',url='https://example.com/post'))
    future=(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat()
    with patch('backend.app.core.platform_adapters.PlatformRegistry.get_adapter',return_value=adapter):
        response=client.post('/api/v1/content/publish-multi',headers=headers,json={'platforms':['x'],'text':'Test schedule','publish_now':False,'scheduled_at':future})
        assert response.status_code==201,response.text
        assert response.json()['overall_status']=='scheduled'
        adapter.publish_post.assert_not_called();adapter.schedule_post.assert_not_called()
        schedule=await async_test_db.scalar(select(Schedule));schedule.scheduled_at=datetime.now(timezone.utc).replace(tzinfo=None)-timedelta(seconds=1)
        await async_test_db.commit()
        first=await SchedulingService(async_test_db).execute_due_schedules()
        second=await SchedulingService(async_test_db).execute_due_schedules()
        assert first['executed']==1 and second['executed']==0
        assert adapter.publish_post.await_count==1


def test_model_promotion_requires_administrator(client):
    _,headers=register(client)
    assert client.post('/api/v1/models/scheduling_rf_gb_ensemble/promote',headers=headers,json={'target_stage':'production','reason':'test'}).status_code==403


def test_validation_errors_do_not_echo_submitted_password(client):
    response=client.post('/api/v1/auth/register',json={'email':'invalid','password':'short-secret','accept_terms':True})
    assert response.status_code==422
    assert 'short-secret' not in response.text


def test_mfa_secret_replacement_and_login_replay_are_rejected(client):
    import pyotp
    _,headers=register(client)
    setup=client.post('/api/v1/auth/2fa/setup',headers=headers).json()
    code=pyotp.TOTP(setup['secret']).now()
    assert client.post('/api/v1/auth/2fa/enable',headers=headers,json={'code':code}).status_code==200
    assert client.post('/api/v1/auth/2fa/setup',headers=headers).status_code==409
    no_code=client.post('/api/v1/auth/login',json={'email':'owner@example.com','password':'Test-password-2984!'})
    assert no_code.json()['requires_2fa'] is True and no_code.json()['access_token']==''
    payload={'email':'owner@example.com','password':'Test-password-2984!','two_factor_code':code}
    assert client.post('/api/v1/auth/login',json=payload).status_code==200
    assert client.post('/api/v1/auth/login',json=payload).status_code==401


@pytest.mark.asyncio
async def test_strategy_feedback_is_persisted_for_owner(client,async_test_db):
    from backend.app.db.models import StrategyFeedback
    data,headers=register(client)
    result=client.post('/api/v1/strategy/feedback',headers=headers,json={'recommendation_id':'timing-review','applied':True,'feedback_notes':'Use cautiously'})
    assert result.status_code==200,result.text
    record=await async_test_db.scalar(select(StrategyFeedback))
    assert str(record.user_id)==data['user']['id'] and record.applied is True


@pytest.mark.asyncio
async def test_analytics_use_latest_owned_snapshot_without_estimates(client,async_test_db):
    from backend.app.db.models import Metric
    data,headers=register(client)
    owner=UUID(data['user']['id'])
    account=SocialAccount(user_id=owner,platform='x',platform_user_id='analytics-owner',account_metadata={'followers_count':12})
    post=Post(user_id=owner,content_type=ContentTypeEnum.POST,status=PostStatusEnum.PUBLISHED,published_at=datetime.now(timezone.utc).replace(tzinfo=None))
    async_test_db.add_all([account,post]);await async_test_db.flush()
    async_test_db.add(PostPublication(post_id=post.id,platform='x',platform_post_id='analytics-post',status='published'))
    now=datetime.now(timezone.utc).replace(tzinfo=None)
    for ago,impressions in [(10,100),(0,150)]:
        async_test_db.add(Metric(post_id=post.id,platform='x',entity_id='analytics-post',entity_type='post',
            metrics={'impressions':impressions,'reach':80,'likes':5,'comments':2},fetched_at=now-timedelta(minutes=ago)))
    await async_test_db.commit()
    result=client.get('/api/v1/analytics/dashboard',headers=headers)
    assert result.status_code==200,result.text
    summary=result.json()
    assert summary['total_impressions']==150 and summary['total_reach']==80 and summary['total_engagements']==7
    comparison=client.get('/api/v1/analytics/comparison',headers=headers)
    assert comparison.status_code==200,comparison.text
    assert comparison.json()['platforms'][0]['impressions']==150


def test_media_url_ssrf_and_credential_protection(client):
    _, headers = register(client)
    # 1. Non-HTTPS URL
    bad_http = client.post('/api/v1/content/publish-multi', headers=headers, json={
        'platforms': ['x'], 'text': 'SSRF test', 'publish_now': True,
        'media': [{'type': 'image', 'url': 'http://example.com/pic.jpg'}]
    })
    assert bad_http.status_code in {400, 422}
    assert 'HTTPS' in bad_http.text

    # 2. Embedded credentials
    bad_cred = client.post('/api/v1/content/publish-multi', headers=headers, json={
        'platforms': ['x'], 'text': 'SSRF test', 'publish_now': True,
        'media': [{'type': 'image', 'url': 'https://admin:pass@example.com/pic.jpg'}]
    })
    assert bad_cred.status_code in {400, 422}

    # 3. Localhost and loopback
    bad_loopback = client.post('/api/v1/content/publish-multi', headers=headers, json={
        'platforms': ['x'], 'text': 'SSRF test', 'publish_now': True,
        'media': [{'type': 'image', 'url': 'https://127.0.0.1/secret.jpg'}]
    })
    assert bad_loopback.status_code in {400, 422}

    # 4. Cloud metadata / private RFC1918
    bad_meta = client.post('/api/v1/content/publish-multi', headers=headers, json={
        'platforms': ['x'], 'text': 'SSRF test', 'publish_now': True,
        'media': [{'type': 'image', 'url': 'https://169.254.169.254/latest/meta-data'}]
    })
    assert bad_meta.status_code in {400, 422}


@pytest.mark.asyncio
async def test_post_and_account_ownership_isolation(client, async_test_db):
    first, h1 = register(client)
    second, h2 = register(client, 'user2@example.com')
    owner = UUID(first['user']['id'])

    post = Post(user_id=owner, content_type=ContentTypeEnum.POST, text="Private Post", status=PostStatusEnum.DRAFT)
    account = SocialAccount(user_id=owner, platform='x', platform_user_id='x_owner', access_token='token')
    async_test_db.add_all([post, account])
    await async_test_db.commit()

    # User 2 cannot read, edit, or delete User 1's post
    assert client.get(f'/api/v1/posts/{post.id}', headers=h2).status_code == 404
    assert client.delete(f'/api/v1/posts/{post.id}', headers=h2).status_code == 404

    # User 2 cannot read or disconnect User 1's social account
    assert client.delete(f'/api/v1/accounts/{account.id}', headers=h2).status_code == 404
    assert client.get(f'/api/v1/accounts/{account.id}', headers=h2).status_code == 404

