// ============================================================
// API URLs — all traffic goes through Traefik on port 80
// ============================================================
const API_URL = 'http://localhost/api/auth';
const REPORT_API_URL = 'http://localhost/api/reports';
const NOTIF_API_URL = 'http://localhost/api/notification';

function getToken() { return localStorage.getItem('access_token'); }
function getUser() { return JSON.parse(localStorage.getItem('user') || '{}'); }

function logout() {
    const refresh = localStorage.getItem('refresh_token');
    const token = localStorage.getItem('access_token');
    if (refresh && token) {
        fetch(`${API_URL}/logout/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ refresh })
        }).catch(() => {});
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

function getUserRole() { return getUser().role || 'user'; }
function isAdmin() { const r = getUserRole(); return r === 'admin' || r === 'superadmin'; }
function isSuperAdmin() { return getUserRole() === 'superadmin'; }
function isUser() { return getUserRole() === 'user'; }

// ============ AUTH ============
async function login(username, password) {
    try {
        const response = await fetch(`${API_URL}/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            localStorage.setItem('user', JSON.stringify(data.user));
            return { success: true, user: data.user };
        }
        return { success: false, error: data.error || 'Identifiants incorrects' };
    } catch (error) {
        return { success: false, error: 'Erreur de connexion au serveur' };
    }
}

async function register(userData) {
    try {
        const response = await fetch(`${API_URL}/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        const data = await response.json();
        if (response.ok) return { success: true, user: data.user };
        return { success: false, error: JSON.stringify(data) };
    } catch (error) {
        return { success: false, error: 'Erreur de connexion au serveur' };
    }
}

async function verifyToken() {
    const token = getToken();
    if (!token) return false;
    try {
        const response = await fetch(`${API_URL}/verify/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.ok;
    } catch { return false; }
}

async function refreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return false;
    try {
        const response = await fetch(`${API_URL}/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh })
        });
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            return true;
        }
        return false;
    } catch { return false; }
}

// ============ USERS (Super Admin) ============
async function getAllUsers() {
    const token = getToken();
    try {
        const response = await fetch(`${API_URL}/users/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) return await response.json();
        return [];
    } catch { return []; }
}

async function createAdmin(userData) {
    const token = getToken();
    try {
        const response = await fetch(`${API_URL}/create-admin/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(userData)
        });
        return response.ok;
    } catch { return false; }
}

async function deleteUser(userId) {
    const token = getToken();
    try {
        const response = await fetch(`${API_URL}/users/${userId}/`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.ok;
    } catch { return false; }
}

async function updateUser(userId, userData) {
    const token = getToken();
    try {
        const response = await fetch(`${API_URL}/users/${userId}/update/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(userData)
        });
        return response.ok;
    } catch { return false; }
}

// ============ REPORTS ============
async function getAllReports() {
    const token = getToken();
    console.log('📡 getAllReports - Fetching from:', `${REPORT_API_URL}/`);
    try {
        const response = await fetch(`${REPORT_API_URL}/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        console.log('📡 getAllReports - Response status:', response.status);
        if (response.ok) {
            const data = await response.json();
            console.log(`✅ getAllReports: ${data.length} reports loaded`);
            return data;
        }
        return [];
    } catch (error) {
        console.error('Erreur getAllReports:', error);
        return [];
    }
}

async function getUserReports() {
    const token = getToken();
    try {
        const response = await fetch(`${REPORT_API_URL}/my_reports/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) return await response.json();
        return [];
    } catch (error) {
        console.error('Erreur getUserReports:', error);
        return [];
    }
}

async function createReport(reportData) {
    const token = getToken();
    
    console.log('🔑 Token:', token ? 'Present' : 'Missing');
    console.log('📦 Report data:', reportData);
    
    if (!token) {
        console.error('❌ No token found');
        return false;
    }
    
    const hasImages = reportData.images && reportData.images.length > 0;
    console.log('📸 Has images:', hasImages);
    
    try {
        let response;
        const url = `${REPORT_API_URL}/`;
        console.log('🌐 URL:', url);
        
        if (hasImages) {
            const formData = new FormData();
            formData.append('description', reportData.description);
            formData.append('latitude', reportData.latitude);
            formData.append('longitude', reportData.longitude);
            formData.append('category', reportData.category);
            formData.append('priority', reportData.priority);
            
            for (let i = 0; i < reportData.images.length; i++) {
                formData.append('uploaded_images', reportData.images[i]);
            }
            
            response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });
        } else {
            const bodyData = {
                description: reportData.description,
                latitude: reportData.latitude,
                longitude: reportData.longitude,
                category: reportData.category,
                priority: reportData.priority
            };
            console.log('📤 Body JSON:', bodyData);
            
            response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(bodyData)
            });
        }
        
        console.log('📡 Response status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Success:', data);
            return true;
        } else {
            const errorText = await response.text();
            console.error('❌ Error response:', errorText);
            return false;
        }
    } catch (error) {
        console.error('❌ Fetch error:', error);
        return false;
    }
}

async function updateReportStatus(reportId, newStatus) {
    const token = getToken();
    try {
        const response = await fetch(`${REPORT_API_URL}/${reportId}/`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ status: newStatus })
        });
        return response.ok;
    } catch (error) {
        console.error('Erreur updateReportStatus:', error);
        return false;
    }
}

// ============ CATEGORIES ============
async function getAllCategories() {
    const token = getToken();
    const url = `${REPORT_API_URL.replace('/reports', '/categories')}/`;
    console.log('Fetching categories from:', url);
    try {
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const data = await response.json();
            console.log('Categories loaded:', data);
            return data;
        }
        return [];
    } catch (error) {
        console.error('Erreur getAllCategories:', error);
        return [];
    }
}

async function createCategory(name) {
    const token = getToken();
    try {
        const response = await fetch(`${REPORT_API_URL.replace('/reports', '/categories')}/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ name })
        });
        return response.ok;
    } catch (error) {
        console.error('Erreur createCategory:', error);
        return false;
    }
}

async function deleteCategory(categoryId) {
    const token = getToken();
    try {
        const response = await fetch(`${REPORT_API_URL.replace('/reports', '/categories')}/${categoryId}/`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.ok;
    } catch (error) {
        console.error('Erreur deleteCategory:', error);
        return false;
    }
}

async function loadCategoriesSelect() {
    const select = document.getElementById('category');
    if (!select) return;
    try {
        const categories = await getAllCategories();
        select.innerHTML = '<option value="">-- Sélectionner une catégorie --</option>';
        categories.forEach(c => {
            select.innerHTML += `<option value="${c.id}">${c.name}</option>`;
        });
    } catch(e) {
        console.error('Erreur loadCategoriesSelect:', e);
    }
}

// ============ NOTIFICATIONS ============
async function getNotifications() {
    const token = getToken();
    try {
        const response = await fetch(`${NOTIF_API_URL}/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) return await response.json();
        return [];
    } catch (error) {
        console.error('Erreur getNotifications:', error);
        return [];
    }
}


async function markNotificationAsRead(notificationId) {
    const token = getToken();
    try {
        // Assure-toi que c'est /read/ et pas /mark_read/
        const response = await fetch(`${NOTIF_API_URL}/${notificationId}/read/`, {
            method: 'PATCH',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.ok;
    } catch (error) {
        console.error('Erreur markNotificationAsRead:', error);
        return false;
    }
}

async function getUnreadCount() {
    try {
        const notifications = await getNotifications();
        return notifications.filter(n => !n.is_read).length;
    } catch { return 0; }
}

// ============ AUTH CHECK ============
function checkAuth() {
    const publicPages = ['login', 'register', 'index'];
    const isPublic = publicPages.some(p => window.location.pathname.includes(p));
    if (!getToken() && !isPublic) {
        window.location.href = 'login.html';
    }
}