#!/usr/bin/env node
/**
 * Standalone Node.js CLI script to test SMTP connection and OTP email delivery.
 *
 * Usage:
 *   node scripts/test-email.cjs test@example.com
 */

const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');

// Basic env parser if dotenv not present
const envPath = path.resolve(__dirname, '../.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  envContent.split('\n').forEach(line => {
    const match = line.match(/^\s*([\w.-]+)\s*=\s*(.*)?\s*$/);
    if (match) {
      const key = match[1];
      let value = match[2] || '';
      if (value.startsWith('"') && value.endsWith('"')) value = value.slice(1, -1);
      if (value.startsWith("'") && value.endsWith("'")) value = value.slice(1, -1);
      if (!process.env[key]) process.env[key] = value.trim();
    }
  });
}

const host = process.env.SMTP_HOST || 'smtp.gmail.com';
const port = parseInt(process.env.SMTP_PORT || '465', 10);
const secure = port === 465;
const user = process.env.SMTP_USER;
const pass = process.env.SMTP_PASSWORD || process.env.SMTP_PASS;
const from = process.env.FROM_EMAIL || user || 'no-reply@aismm.ai';
const recipient = process.argv[2];

console.log("\n========================================================");
console.log(" 📧 Node.js SMTP Transport Diagnostic Tool");
console.log("========================================================");
console.log(`Host:    ${host}`);
console.log(`Port:    ${port} (${secure ? 'SSL' : 'STARTTLS'})`);
console.log(`User:    ${user || '[NOT SET]'}`);
console.log(`From:    ${from}`);
console.log("--------------------------------------------------------");

if (!user || !pass) {
  console.error("❌ SMTP_USER or SMTP_PASSWORD / SMTP_PASS is missing in .env.");
  process.exit(1);
}

const transporter = nodemailer.createTransport({
  host,
  port,
  secure,
  auth: { user, pass },
  tls: { rejectUnauthorized: false }
});

transporter.verify(async (err, success) => {
  if (err) {
    console.error("❌ SMTP Connection Failed:", err.message);
    process.exit(1);
  }
  console.log("✅ SMTP Connection Successful! Ready to send emails.");

  if (!recipient) {
    console.log("\n💡 To send a test email, run: node scripts/test-email.cjs your_email@example.com");
    process.exit(0);
  }

  const testOtp = "729401";
  console.log(`\n📨 Sending test OTP email (${testOtp}) to ${recipient}...`);

  try {
    const info = await transporter.sendMail({
      from: `"AISMM Security" <${from}>`,
      to: recipient,
      subject: `Your AISMM Verification Code: ${testOtp} (Expires in 10 minutes)`,
      text: `Hi,\n\nYour AISMM verification code is: ${testOtp}\n\nThis code expires in 10 minutes.`,
      html: `
        <div style="font-family:sans-serif;background:#0d121f;color:#cbd5e1;padding:30px;border-radius:12px;max-width:500px;">
          <h2 style="color:#ffffff;">AISMM Verification Code</h2>
          <p>Please enter the code below to verify your account:</p>
          <div style="background:#07090e;border:1px solid #334155;border-radius:8px;padding:16px;text-align:center;margin:20px 0;">
            <span style="font-size:32px;font-weight:bold;letter-spacing:6px;color:#38bdf8;font-family:monospace;">${testOtp}</span>
          </div>
          <p style="color:#64748b;font-size:12px;">This code expires in 10 minutes.</p>
        </div>
      `
    });
    console.log(`✅ Email delivered! Message ID: ${info.messageId}`);
  } catch (sendErr) {
    console.error("❌ Failed to send email:", sendErr.message);
    process.exit(1);
  }
});
