<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount } from 'vue';

// Убираем глобальную загрузку данных из App.vue
// Данные будут загружаться только в конкретных компонентах где нужны

onBeforeMount(() => {
  // Настраиваем axios только один раз
  const csrfToken = Cookies.get("csrftoken");
  if (csrfToken) {
    axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
  }
  axios.defaults.withCredentials = true;
  
  // Опционально: настраиваем таймауты
  axios.defaults.timeout = 10000; // 10 секунд
})
</script>

<template>
  <div id="app">
    <!-- Навигация -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          🏆 Турнирная Система
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">
                <i class="bi bi-house me-1"></i>Главная
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/teams">
                <i class="bi bi-people me-1"></i>Команды
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/players">
                <i class="bi bi-person me-1"></i>Игроки
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/tournaments">
                <i class="bi bi-trophy me-1"></i>Турниры
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/categories">
                <i class="bi bi-tags me-1"></i>Категории
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/matches">
                <i class="bi bi-controller me-1"></i>Матчи
              </router-link>
            </li>
          </ul>
          
          <ul class="navbar-nav">
            <li class="nav-item">
              <a class="nav-link" href="/admin" target="_blank">
                <i class="bi bi-gear me-1"></i>Админка
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Основной контент -->
    <main class="main-content">
      <router-view/>
    </main>
  </div>
</template>

<style scoped>
.navbar-brand {
  font-weight: bold;
  font-size: 1.3rem;
}

.nav-link {
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 5px;
  font-weight: bold;
}

.main-content {
  min-height: calc(100vh - 76px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>