// Configuration
const API_URL = 'http://localhost:8000/api';
const REPORT_API_URL = 'http://localhost:8001/api';
const NOTIF_API_URL = 'http://localhost:5000';  
function getToken() {
    return localStorage.getItem('access_token');
}

function getUser() {
    return JSON.parse(localStorage.getItem('user') || '{}');
}

function logout() {
    const refresh = localStorage.getItem('refresh_token');
    const token = localStorage.getItem('access_token');

    // Send refresh token to server to blacklist it
    if (refresh && token) {
        fetch(`${API_URL}/logout/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ refresh: refresh })
        }).catch(() => {}); // Don't block UI if this fails
    }

    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

function getUserRole() {
    const user = getUser();
    return user.role || 'user';
}

function isAdmin() {
    const role = getUserRole();
    return role === 'admin' || role === 'superadmin';
}

function isSuperAdmin() {
    return getUserRole() === 'superadmin';
}

function isUser() {
    return getUserRole() === 'user';
}

// ============ AUTHENTIFICATION ============
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
        } else {
            return { success: false, error: data.error || 'Identifiants incorrects' };
        }
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
        
        if (response.ok) {
            return { success: true, user: data.user };
        } else {
            return { success: false, error: JSON.stringify(data) };
        }
    } catch (error) {
        return { success: false, error: 'Erreur de connexion au serveur' };
    }
}

async function verifyToken() {
    const token = getToken();
    if (!token) return false;
    
    try {
        const response = await fetch(`${API_URL}/verify/`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.ok;
    } catch (error) {
        return false;
    }
}

// ============ GESTION DES UTILISATEURS (Super Admin) ============
async function getAllUsers() {
    const token = getToken();
    try {
        const response = await fetch(`${API_URL}/users/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            return await response.json();
        }
        return [];
    } catch (error) {
        return [];
    }
}

async function createAdmin(userData) {
    const token = getToken();
    try {
        const response = await fetch(`${API_URL}/create-admin/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(userData)
        });
        return response.ok;
    } catch (error) {
        return false;
    }
}

async function deleteUser(userId) {
    const token = getToken();
    try {
        const response = await fetch(`${API_URL}/users/${userId}/`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return response.ok;
    } catch (error) {
        return false;
    }
}

async function updateUser(userId, userData) {
    const token = getToken();
    try {
        const response = await fetch(`${API_URL}/users/${userId}/update/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(userData)
        });
        return response.ok;
    } catch (error) {
        return false;
    }
}

// ============ GESTION DES SIGNALEMENTS ============
// script.js - Ajouter cette fonction

async function refreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return false;
    
    try {
        const response = await fetch(`${API_URL}/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refresh })
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            console.log('✅ Token refreshed successfully');
            return true;
        }
        return false;
    } catch (error) {
        console.error('❌ Token refresh failed:', error);
        return false;
    }
}
// script.js - Remplacer getAllReports
async function getAllReports() {
    const token = getToken();
    if (!token) {
        console.error('❌ getAllReports: No token found');
        return [];
    }
    
    try {
        console.log('📡 getAllReports - Fetching from:', `${REPORT_API_URL}/reports/`);
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);
        
        const response = await fetch(`${REPORT_API_URL}/reports/`, {
            method: 'GET',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        console.log('📡 getAllReports - Response status:', response.status);
        
        if (response.status === 401) {
            console.log('🔄 Token expired, trying to refresh...');
            const refreshed = await refreshToken();
            if (refreshed) {
                return getAllReports();
            } else {
                // Token refresh failed, redirect to login
                logout();
                return [];
            }
        }
        
        if (!response.ok) {
            console.error('❌ getAllReports failed with status:', response.status);
            return [];
        }
        
        const data = await response.json();
        console.log(`✅ getAllReports: ${data.length} reports loaded`);
        return data;
        
    } catch (error) {
        if (error.name === 'AbortError') {
            console.error('❌ getAllReports timeout');
        } else {
            console.error('❌ getAllReports fetch error:', error);
        }
        return [];
    }
}
async function getUserReports() {
    const token = getToken();
    try {
        const response = await fetch(`${REPORT_API_URL}/reports/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const allReports = await response.json();
            const user = getUser();
            return allReports.filter(r => r.user_id === user.id);
        }
        return [];
    } catch (error) {
        console.error('Erreur getUserReports:', error);
        return [];
    }
}

// script.js - Remplacer la fonction createReport par celle-ci

async function createReport(reportData) {
    const token = getToken();
    if (!token) {
        console.error('❌ No token found');
        return false;
    }
    
    console.log('📤 Creating report with data:', reportData);
    
    // TOUJOURS utiliser FormData pour éviter les problèmes CORS
    const formData = new FormData();
    formData.append('description', reportData.description);
    formData.append('latitude', reportData.latitude);
    formData.append('longitude', reportData.longitude);
    formData.append('category', reportData.category);
    formData.append('priority', reportData.priority || 'medium');
    
    // Ajouter les images si présentes
    if (reportData.images && reportData.images.length > 0) {
        for (let i = 0; i < reportData.images.length; i++) {
            formData.append('uploaded_images', reportData.images[i]);
        }
    }
    
    try {
        console.log('📡 Sending request to:', `${REPORT_API_URL}/reports/`);
        
        const response = await fetch(`${REPORT_API_URL}/reports/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
                // ⚠️ NE PAS mettre Content-Type avec FormData - le navigateur le définit automatiquement
            },
            body: formData
        });
        
        console.log('📡 Response status:', response.status);
        
        if (response.ok) {
            // Lire la réponse (optionnel)
            const data = await response.json().catch(() => ({}));
            console.log('✅ Report created successfully:', data);
            return true;
        } else {
            const errorText = await response.text();
            console.error('❌ Server error:', response.status, errorText);
            return false;
        }
    } catch (error) {
        console.error('❌ Fetch error:', error);
        return false;
    }
}

async function updateReportStatus(reportId, status) {
    const token = getToken();
    try {
        const response = await fetch(`${REPORT_API_URL}/reports/${reportId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ status })
        });
        return response.ok;
    } catch (error) {
        console.error('Erreur updateReportStatus:', error);
        return false;
    }
}

// ============ CHECK AUTH ============
function checkAuth() {
    if (!getToken() && !window.location.pathname.includes('login') && !window.location.pathname.includes('register') && !window.location.pathname.includes('index')) {
        window.location.href = 'login.html';
    }
}
// ============ GESTION DES NOTIFICATIONS ============
async function getNotifications(userId) {
    const token = getToken();
    try {
        const response = await fetch(`http://localhost:5000/api/notification/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const data = await response.json();
            // Filtrer par user_id si nécessaire
            return data.filter(n => n.user_id === userId);
        }
        return [];
    } catch (error) {
        console.error('Erreur getNotifications:', error);
        return [];
    }
}

async function markNotificationAsRead(notificationId) {
    const token = getToken();
    try {
        const response = await fetch(`http://localhost:5000/api/notification/${notificationId}/mark_read/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });
        return response.ok;
    } catch (error) {
        console.error('Erreur markNotificationAsRead:', error);
        return false;
    }
}
async function getUnreadCount(userId) {
    const notifications = await getNotifications(userId);
    return notifications.filter(n => !n.read).length;
}

// ============ GESTION DES CATÉGORIES (Super Admin) ============
// script.js - Modifier getAllCategories
async function getAllCategories() {
    const token = getToken();
    try {
        console.log('Fetching categories from:', `${REPORT_API_URL}/categories/`);
        
        // ✅ Ajouter un timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);
        
        const response = await fetch(`${REPORT_API_URL}/categories/`, {
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Categories loaded:', data);
            return data;
        } else {
            console.error('Response not OK:', response.status, response.statusText);
            return [];
        }
    } catch (error) {
        console.error('Erreur getAllCategories:', error);
        // ✅ Retourner des catégories par défaut si le service est inaccessible
        return [
            { id: 1, name: "🚧 Routes" },
            { id: 2, name: "💡 Éclairage public" },
            { id: 3, name: "🗑️ Déchets" },
            { id: 4, name: "🌳 Espaces verts" },
            { id: 5, name: "🚰 Eau et assainissement" },
            { id: 6, name: "🚦 Signalisation" }
        ];
    }
}

async function createCategory(name) {
    const token = getToken();
    try {
        const response = await fetch(`${REPORT_API_URL}/categories/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ name: name })
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
        const response = await fetch(`${REPORT_API_URL}/categories/${categoryId}/`, {
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
        console.error(e);
    }
}

