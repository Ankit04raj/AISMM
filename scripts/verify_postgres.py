"""Run against an already-running disposable development API backed by PostgreSQL.
Never point this test at a production customer database.
"""
import os, secrets, uuid, httpx
base=os.environ.get('TEST_API_URL','http://127.0.0.1:8001/api/v1')
email=f'postgres-qa-{uuid.uuid4().hex}@example.com'
password=secrets.token_urlsafe(24)
checks=[]
with httpx.Client(base_url=base,timeout=30) as client:
    def check(label,response,status):
        assert response.status_code==status,f'{label}: {response.status_code} {response.text[:200]}'
        checks.append(label);return response.json()
    data=check('register',client.post('/auth/register',json={'email':email,'password':password,'accept_terms':True}),201)
    headers={'Authorization':'Bearer '+data['access_token']}
    check('unverified gate',client.get('/accounts',headers=headers),403)
    check('email verification',client.post('/auth/verify-email',headers=headers,json={'token':data['verification_token']}),200)
    for route in ['/accounts','/posts','/comments','/analytics/dashboard']:
        check('authenticated '+route,client.get(route,headers=headers),200)
    check('profile persistence',client.patch('/auth/me',headers=headers,json={'full_name':'PostgreSQL QA'}),200)
    check('2fa setup',client.post('/auth/2fa/setup',headers=headers),200)
    rotated=check('refresh rotation',client.post('/auth/refresh',json={'refresh_token':data['refresh_token']}),200)
    check('refresh replay rejected',client.post('/auth/refresh',json={'refresh_token':data['refresh_token']}),401)
    check('logout',client.post('/auth/logout',headers=headers,json={}),200)
    check('revoked access rejected',client.get('/auth/me',headers={'Authorization':'Bearer '+rotated['access_token']}),401)
    check('revoked refresh rejected',client.post('/auth/refresh',json={'refresh_token':rotated['refresh_token']}),401)
print(f'{len(checks)} PostgreSQL-backed real HTTP checks passed')
print('\n'.join('PASS '+label for label in checks))
