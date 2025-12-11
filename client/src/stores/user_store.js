import {defineStore} from "pinia";
import {onBeforeMount, ref} from "vue";
import axios from "axios";

export const useUserStore = defineStore("userStore", () => {
    const userInfo = ref({
        is_authenticated: false
    })
    const second = ref(false);  
    async function checkLogin() {
        try {
            let r = await axios.get("/api/user/info/")
            userInfo.value = r.data;
            second.value = r.data.second;
        } catch (error) {
            userInfo.value = {
                is_authenticated: false,
                second: false    
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
                second: false,
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
        second,
        logout,
    }
})