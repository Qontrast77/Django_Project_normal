import {defineStore} from "pinia";
import {onBeforeMount, ref} from "vue";
import axios from "axios";

export const useUserStore = defineStore("userStore", () => {
    const userInfo = ref({
        is_authenticated: false
    })
    
    async function checkLogin() {
        try {
            let r = await axios.get("/api/user/info/")
            userInfo.value = r.data;
            console.log("User info loaded:", userInfo.value); // Добавлено для отладки
        } catch (error) {
            console.error("Error loading user info:", error);
            userInfo.value = {
                is_authenticated: false
            };
        }
    }

    async function login(username, password) {
        try {
            let r = await axios.post("/api/user/login/", {
                username: username,
                password: password,
            })
            
            if (r.data.success) {
                // Обновляем userInfo данными с сервера
                if (r.data.user_info) {
                    userInfo.value = r.data.user_info;
                } else {
                    await checkLogin();
                }
                return { success: true };
            } else {
                return { success: false, error: r.data.error };
            }
        } catch (error) {
            console.error("Login error:", error);
            return { success: false, error: "Ошибка соединения" };
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
                username: "",
                is_staff: false
            };
        }
    }

    onBeforeMount(async () => {
        await checkLogin();
    })

    return {
        userInfo,
        checkLogin,
        login,
        logout
    }
})