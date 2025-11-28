import {defineStore} from "pinia";
import {onBeforeMount, ref} from "vue";
import axios from "axios";

export const useUserStore = defineStore("userStore", () => {
    const userInfo = ref({
        is_authenticated: false,
        is_doublefaq: false
    })
    
    async function checkLogin() {
        try {
            let r = await axios.get("/api/user/info/")
            userInfo.value = r.data;
        } catch (error) {
            userInfo.value = {
                is_authenticated: false,
                is_doublefaq: false
            };
        }
    }

    async function login(username, password) {
        try {
            let r = await axios.post("/api/user/login/", {
                username: username,
                password: password,
            })
            await checkLogin();
            return r.data.success;
        } catch (error) {
            console.error("Login error:", error);
            return false;
        }
    }

    async function logout() {
        try {
            await axios.post("/api/user/logout/");
        } catch (error) {
            console.error("Logout error:", error);
        } finally {
            userInfo.value = {
                is_authenticated: false,
                is_doublefaq: false
            };
        }
    }

    // Генерация кода 2FA на сервере
    async function generate2FACode() {
        try {
            let r = await axios.post("/api/user/generate-2fa/")
            return r.data
        } catch (error) {
            return { success: false, message: 'Ошибка при генерации кода' }
        }
    }

    // Проверка кода 2FA на сервере
    async function verify2FACode(inputCode) {
        try {
            let r = await axios.post("/api/user/verify-2fa/", {
                code: inputCode,
            })
            
            if (r.data.success) {
                await checkLogin(); // Обновляем статус
            }
            
            return r.data
        } catch (error) {
            return { success: false, message: 'Ошибка при проверке кода' }
        }
    }

    onBeforeMount(async () => {
        await checkLogin();
    })

    return {
        userInfo,
        checkLogin,
        login,
        logout,
        generate2FACode,
        verify2FACode
    }
})