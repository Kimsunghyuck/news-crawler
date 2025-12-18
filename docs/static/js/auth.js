// Firebase Google Sign-in Authentication
// https://firebase.google.com/docs/auth/web/google-signin

import { initializeApp } from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js';
import {
    getAuth,
    GoogleAuthProvider,
    signInWithPopup,
    onAuthStateChanged
} from 'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js';

// ===== Firebase Configuration =====
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
    showError('Firebase 설정을 확인해주세요.');
}

// ===== DOM Elements =====
const authLanding = document.getElementById('auth-landing');
const authLoading = document.getElementById('auth-loading');
const authError = document.getElementById('auth-error');
const authErrorText = document.getElementById('auth-error-text');
const authLoadingText = document.getElementById('auth-loading-text');
const googleSigninBtn = document.getElementById('google-signin-btn');

// ===== Google Sign-in Event Listener =====
if (googleSigninBtn) {
    googleSigninBtn.addEventListener('click', async () => {
        await signInWithGoogle();
    });
}

// ===== Logout Button Event Listener =====
const logoutBtn = document.getElementById('logout-btn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
        if (confirm('로그아웃 하시겠습니까?')) {
            try {
                await auth.signOut();
                console.log('✅ User signed out successfully');
                window.location.reload();
            } catch (error) {
                console.error('❌ Sign out error:', error);
                alert('로그아웃에 실패했습니다. 다시 시도해주세요.');
            }
        }
    });
}

// ===== Authentication Functions =====

async function signInWithGoogle() {
    showLoading('Google 로그인 중...');
    clearError();

    const provider = new GoogleAuthProvider();

    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;

        console.log('✅ User signed in:', user.email);
        console.log('   Display name:', user.displayName);
        console.log('   User ID:', user.uid);

        hideLoading();
        hideAuthLanding();

    } catch (error) {
        console.error('❌ Google sign-in error:', error);
        console.error('Error code:', error.code);
        console.error('Error message:', error.message);
        hideLoading();

        let errorMessage = 'Google 로그인에 실패했습니다.';

        if (error.code === 'auth/popup-closed-by-user') {
            errorMessage = '로그인 창이 닫혔습니다. 다시 시도해주세요.';
        } else if (error.code === 'auth/popup-blocked') {
            errorMessage = '팝업이 차단되었습니다. 브라우저 설정에서 팝업을 허용해주세요.';
        } else if (error.code === 'auth/cancelled-popup-request') {
            // 사용자가 여러 번 클릭한 경우 - 에러 표시 안 함
            return;
        } else if (error.code === 'auth/unauthorized-domain') {
            errorMessage = 'Firebase 콘솔에서 현재 도메인을 승인된 도메인에 추가해주세요.';
        } else if (error.code === 'auth/operation-not-allowed') {
            errorMessage = 'Firebase 콘솔에서 Google 로그인을 활성화해주세요.';
        }

        showError(errorMessage);
    }
}

// ===== UI Helper Functions =====

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
    document.body.style.overflow = 'auto';
    console.log('✅ Authentication complete - Main site unlocked');
}

function showAuthLanding() {
    authLanding.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

// ===== Test Environment Bypass =====

function isTestEnvironment() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('skipAuth') === 'true';
}

// ===== Auth State Observer =====

onAuthStateChanged(auth, (user) => {
    if (user) {
        console.log('👤 User is signed in:', user.email);
        console.log('   Display name:', user.displayName);
        hideAuthLanding();
    } else {
        console.log('👤 User is signed out');

        // Check if test environment - bypass auth
        if (isTestEnvironment()) {
            console.log('🧪 Test environment detected - bypassing authentication');
            hideAuthLanding();
        } else {
            // Show auth landing if not authenticated and not in test mode
            showAuthLanding();
        }
    }
});

// ===== Export for debugging =====
window.firebaseAuth = {
    auth,
    currentUser: () => auth.currentUser,
    signOut: () => auth.signOut()
};

console.log('🔐 Firebase Auth module loaded (Google Sign-in)');
console.log('💡 Tip: Use window.firebaseAuth.signOut() to log out');
console.log('💡 Tip: Use ?skipAuth=true to bypass authentication (dev only)');
