// Firebase Email Link Authentication
// https://firebase.google.com/docs/auth/web/email-link-auth

import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import {
    getAuth,
    sendSignInLinkToEmail,
    isSignInWithEmailLink,
    signInWithEmailLink,
    onAuthStateChanged
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';

// ===== Firebase Configuration =====
// IMPORTANT: Firebase config를 입력해주세요!
// FIREBASE_SETUP.md 가이드를 따라 Firebase 프로젝트를 생성하고 아래 값을 입력하세요.
const firebaseConfig = {
    apiKey: "AIzaSyDA_4iqiPRv0QJQS_vEkTHjqtd7XtF2wZ4",
    authDomain: "hyeok-news-crawler.firebaseapp.com",
    projectId: "hyeok-news-crawler",
    storageBucket: "hyeok-news-crawler.firebasestorage.app",
    messagingSenderId: "792473801664",
    appId: "1:792473801664:web:34c6b9ea4ec7bcff3f2e25"
};

// Firebase 초기화
let app, auth;
try {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    console.log('✅ Firebase initialized successfully');
} catch (error) {
    console.error('❌ Firebase initialization failed:', error);
    showError('Firebase 설정을 확인해주세요. FIREBASE_SETUP.md를 참고하세요.');
}

// ===== DOM Elements =====
const authLanding = document.getElementById('auth-landing');
const authStepEmail = document.getElementById('auth-step-email');
const authStepInput = document.getElementById('auth-step-input');
const authStepWaiting = document.getElementById('auth-step-waiting');
const authLoading = document.getElementById('auth-loading');
const authError = document.getElementById('auth-error');
const authErrorText = document.getElementById('auth-error-text');
const authLoadingText = document.getElementById('auth-loading-text');

const enterSiteBtn = document.getElementById('enter-site-btn');
const emailForm = document.getElementById('email-form');
const emailInput = document.getElementById('email-input');
const backToEnterBtn = document.getElementById('back-to-enter-btn');
const backToEmailBtn = document.getElementById('back-to-email-btn');
const resendLinkBtn = document.getElementById('resend-link-btn');
const displayEmail = document.getElementById('display-email');

// ===== Email Link Configuration =====
const actionCodeSettings = {
    // URL to redirect back to after email link is clicked
    // For local development: http://localhost:8000
    // For GitHub Pages: https://kimsunghyuck.github.io/news-crawler/
    url: 'https://kimsunghyuck.github.io/news-crawler/',
    handleCodeInApp: true,
};

// ===== State Management =====
let currentEmail = '';
let lastEmailSentTime = 0;
const EMAIL_COOLDOWN_MS = 60000; // 60 seconds cooldown

// ===== Event Listeners =====
enterSiteBtn.addEventListener('click', () => {
    switchStep('input');
});

emailForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = emailInput.value.trim();

    if (!email) {
        showError('이메일을 입력해주세요.');
        return;
    }

    await sendEmailLink(email);
});

backToEnterBtn.addEventListener('click', () => {
    switchStep('email');
    clearError();
});

backToEmailBtn.addEventListener('click', () => {
    switchStep('input');
    clearError();
});

resendLinkBtn.addEventListener('click', async () => {
    if (currentEmail) {
        const now = Date.now();
        const timeSinceLastEmail = now - lastEmailSentTime;

        if (timeSinceLastEmail < EMAIL_COOLDOWN_MS) {
            const remainingSeconds = Math.ceil((EMAIL_COOLDOWN_MS - timeSinceLastEmail) / 1000);
            showError(`너무 빠르게 재전송을 시도했습니다. ${remainingSeconds}초 후에 다시 시도해주세요.`);
            startResendCooldown();
            return;
        }

        await sendEmailLink(currentEmail);
    }
});

// Start cooldown timer for resend button
function startResendCooldown() {
    resendLinkBtn.disabled = true;
    const originalText = resendLinkBtn.textContent;

    const updateTimer = () => {
        const now = Date.now();
        const timeSinceLastEmail = now - lastEmailSentTime;
        const remainingMs = EMAIL_COOLDOWN_MS - timeSinceLastEmail;

        if (remainingMs <= 0) {
            resendLinkBtn.disabled = false;
            resendLinkBtn.textContent = originalText;
            return;
        }

        const remainingSeconds = Math.ceil(remainingMs / 1000);
        resendLinkBtn.textContent = `${originalText} (${remainingSeconds}초)`;
        setTimeout(updateTimer, 1000);
    };

    updateTimer();
}

// ===== Authentication Functions =====

async function sendEmailLink(email) {
    showLoading('이메일 전송 중...');
    clearError();

    try {
        console.log('📤 Sending email link to:', email);
        await sendSignInLinkToEmail(auth, email, actionCodeSettings);

        // Update last sent time
        lastEmailSentTime = Date.now();

        // Save email to localStorage for verification after redirect
        window.localStorage.setItem('emailForSignIn', email);
        currentEmail = email;

        // Show waiting step
        displayEmail.textContent = email;
        hideLoading();
        switchStep('waiting');

        console.log('✅ Email link sent successfully to:', email);
        console.log('⏱️ Next email can be sent after:', new Date(lastEmailSentTime + EMAIL_COOLDOWN_MS).toLocaleTimeString());

        // Start cooldown timer for resend button
        startResendCooldown();
    } catch (error) {
        console.error('❌ Send email link error:', error);
        console.error('Error code:', error.code);
        console.error('Error message:', error.message);
        hideLoading();

        let errorMessage = '이메일 전송에 실패했습니다.';

        if (error.code === 'auth/invalid-email') {
            errorMessage = '올바른 이메일 주소를 입력해주세요.';
        } else if (error.code === 'auth/unauthorized-domain') {
            errorMessage = 'Firebase 콘솔에서 현재 도메인을 승인된 도메인에 추가해주세요.';
        } else if (error.code === 'auth/quota-exceeded') {
            errorMessage = '⚠️ Firebase 이메일 전송 한도를 초과했습니다.\n\n원인:\n• 짧은 시간에 너무 많은 이메일 요청\n• 하루 최대 100건 제한 (Spark 플랜)\n\n해결 방법:\n• 60초 후에 다시 시도\n• 또는 내일 다시 시도\n• 또는 Firebase Console에서 Blaze 플랜으로 업그레이드';
            console.error('🚨 QUOTA EXCEEDED - Details:');
            console.error('  - Last email sent:', new Date(lastEmailSentTime).toLocaleString());
            console.error('  - Time since last email:', Math.floor((Date.now() - lastEmailSentTime) / 1000), 'seconds');
            console.error('  - Cooldown period:', EMAIL_COOLDOWN_MS / 1000, 'seconds');
        } else if (error.code === 'auth/too-many-requests') {
            errorMessage = '⚠️ 너무 많은 요청이 발생했습니다.\n60초 후에 다시 시도해주세요.';
        }

        showError(errorMessage);
    }
}

async function completeSignIn(email, emailLink) {
    showLoading('로그인 중...');
    clearError();

    try {
        const result = await signInWithEmailLink(auth, email, emailLink);
        console.log('✅ User signed in:', result.user.email);

        // Clear email from localStorage
        window.localStorage.removeItem('emailForSignIn');

        // Hide auth landing page
        setTimeout(() => {
            hideAuthLanding();
        }, 500);

    } catch (error) {
        console.error('❌ Sign in error:', error);
        hideLoading();

        let errorMessage = '로그인에 실패했습니다.';

        if (error.code === 'auth/invalid-action-code') {
            errorMessage = '인증 링크가 만료되었거나 이미 사용되었습니다. 새로운 링크를 요청해주세요.';
        } else if (error.code === 'auth/invalid-email') {
            errorMessage = '이메일이 일치하지 않습니다.';
        }

        showError(errorMessage);
        switchStep('input');
    }
}

// ===== UI Helper Functions =====

function switchStep(step) {
    authStepEmail.classList.remove('active');
    authStepInput.classList.remove('active');
    authStepWaiting.classList.remove('active');

    if (step === 'email') {
        authStepEmail.classList.add('active');
    } else if (step === 'input') {
        authStepInput.classList.add('active');
        emailInput.focus();
    } else if (step === 'waiting') {
        authStepWaiting.classList.add('active');
    }
}

function showLoading(message = '처리 중...') {
    authLoadingText.textContent = message;
    authLoading.classList.add('active');
}

function hideLoading() {
    authLoading.classList.remove('active');
}

function showError(message) {
    authErrorText.textContent = message;
    authError.classList.add('active');
}

function clearError() {
    authError.classList.remove('active');
}

function hideAuthLanding() {
    authLanding.classList.add('hidden');
    console.log('✅ Authentication complete - Main site unlocked');
}

// ===== Test Environment Bypass =====

// Check if skipAuth parameter is present (for E2E testing)
function isTestEnvironment() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('skipAuth') === 'true';
}

// ===== Auth State Observer =====

onAuthStateChanged(auth, (user) => {
    if (user) {
        console.log('👤 User is signed in:', user.email);
        hideAuthLanding();
    } else {
        console.log('👤 User is signed out');

        // Check if test environment - bypass auth
        if (isTestEnvironment()) {
            console.log('🧪 Test environment detected - bypassing authentication');
            hideAuthLanding();
        } else {
            // Show auth landing if not authenticated and not in test mode
            authLanding.classList.remove('hidden');
        }
    }
});

// ===== Check for Email Link on Page Load =====

window.addEventListener('DOMContentLoaded', () => {
    // Check if user clicked email link
    if (isSignInWithEmailLink(auth, window.location.href)) {
        console.log('📧 Email link detected');

        // Get email from localStorage
        let email = window.localStorage.getItem('emailForSignIn');

        if (!email) {
            // Prompt user to enter email if not found
            email = window.prompt('확인을 위해 이메일 주소를 입력해주세요:');
        }

        if (email) {
            completeSignIn(email, window.location.href);
        }
    }
});

// ===== Export for debugging =====
window.firebaseAuth = {
    auth,
    currentUser: () => auth.currentUser,
    signOut: () => auth.signOut()
};

console.log('🔐 Firebase Auth module loaded');
console.log('💡 Tip: Use window.firebaseAuth.signOut() to log out');
