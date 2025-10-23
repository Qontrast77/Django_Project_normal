<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref } from 'vue';

const teams = ref([]);
const isLoading = ref(false);
const error = ref(null);

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

async function fetchTeams() {
    try {
        isLoading.value = true;
        error.value = null;
        const response = await axios.get("/api/teams/");
        teams.value = response.data;
    } catch (err) {
        console.error('Ошибка загрузки команд:', err);
        error.value = err.response?.data || 'Не удалось загрузить команды';
        teams.value = [];
    } finally {
        isLoading.value = false;
    }
}

onBeforeMount(async () => {
    await fetchTeams();
})

const teamToAdd = ref({});
const teamLogoRef = ref();
const teamImageUrl = ref();

function teamLogoChange() {
  if (teamLogoRef.value.files[0]) {
    teamImageUrl.value = URL.createObjectURL(teamLogoRef.value.files[0]);
  }
}

async function onTeamAdd() {
  try {
    isLoading.value = true;
    const formData = new FormData();
    formData.set('name', teamToAdd.value.name || '');
    
    if (teamLogoRef.value.files[0]) {
      formData.append('logo', teamLogoRef.value.files[0]);
    }
    
    await axios.post("/api/teams/", formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    await fetchTeams();
    teamToAdd.value = {};
    teamImageUrl.value = null;
    if (teamLogoRef.value) {
      teamLogoRef.value.value = '';
    }
  } catch (err) {
    console.error('Ошибка добавления команды:', err);
    error.value = err.response?.data || 'Не удалось добавить команду';
  } finally {
    isLoading.value = false;
  }
}

async function onRemoveClick(team) {
  if (!confirm(`Удалить команду "${team.name}"?`)) return;
  
  try {
    await axios.delete(`/api/teams/${team.id}/`);
    await fetchTeams();
  } catch (err) {
    console.error('Ошибка удаления команды:', err);
    error.value = err.response?.data || 'Не удалось удалить команду';
  }
}

const teamToEdit = ref({});
const teamEditLogoRef = ref();
const teamEditImageUrl = ref();

function teamEditLogoChange() {
  if (teamEditLogoRef.value.files[0]) {
    teamEditImageUrl.value = URL.createObjectURL(teamEditLogoRef.value.files[0]);
  }
}

function onTeamEditClick(team) {
  teamToEdit.value = { ...team };
  teamEditImageUrl.value = null;
}

async function onUpdateTeam() {
  try {
    isLoading.value = true;
    const formData = new FormData();
    formData.set('name', teamToEdit.value.name || '');
    
    if (teamEditLogoRef.value.files[0]) {
      formData.append('logo', teamEditLogoRef.value.files[0]);
    }
    
    await axios.put(`/api/teams/${teamToEdit.value.id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    await fetchTeams();
  } catch (err) {
    console.error('Ошибка обновления команды:', err);
    error.value = err.response?.data || 'Не удалось обновить команду';
  } finally {
    isLoading.value = false;
  }
}

// Улучшенная функция для получения URL изображения
function getImageUrl(imagePath) {
  if (!imagePath) return null;
  
  // Если это уже полный URL, возвращаем как есть
  if (imagePath.startsWith('http') || imagePath.startsWith('data:')) {
    return imagePath;
  }
  
  // Если это относительный путь, добавляем базовый URL
  return imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
}

// Обработчик ошибок изображений - предотвращает цикл
function handleImageError(event) {
  console.log('Изображение не загружено:', event.target.src);
  event.target.style.display = 'none';
  event.target.onerror = null; // Убираем обработчик чтобы избежать цикла
}
</script>

<template>
  <div class="container-fluid">
    <!-- Состояния загрузки и ошибок -->
    <div v-if="isLoading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p class="mt-2 text-muted">Загрузка...</p>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>Ошибка!</strong> {{ error }}
      <button type="button" class="btn-close" @click="error = null"></button>
    </div>

    <!-- Форма добавления команды -->
    <div class="card mb-4">
      <div class="card-header bg-primary text-white">
        <h3 class="mb-0">Добавить команду</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent.stop="onTeamAdd">
          <div class="row g-3">
            <div class="col-md-6">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="teamToAdd.name"
                  placeholder="Название команды"
                  required
                  :disabled="isLoading"
                />
                <label>Название команды</label>
              </div>
            </div>
            <div class="col-md-4">
              <div class="form-floating">
                <input
                  type="file"
                  class="form-control"
                  ref="teamLogoRef"
                  @change="teamLogoChange"
                  accept="image/*"
                  :disabled="isLoading"
                />
                <label>Логотип команды</label>
              </div>
            </div>
            <div class="col-md-2">
              <button class="btn btn-primary h-100 w-100" :disabled="isLoading">
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                Добавить
              </button>
            </div>
          </div>
          
          <!-- Предпросмотр изображения -->
          <div v-if="teamImageUrl" class="mt-3">
            <p class="text-muted mb-2">Предпросмотр:</p>
            <img 
              :src="teamImageUrl" 
              alt="Предпросмотр логотипа"
              class="img-thumbnail"
              style="max-width: 200px; max-height: 200px; object-fit: contain;"
            />
          </div>
        </form>
      </div>
    </div>

    <!-- Список команд -->
    <div class="card">
      <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <h3 class="mb-0">Список команд</h3>
        <span class="badge bg-primary">{{ teams.length }} команд</span>
      </div>
      <div class="card-body">
        <div v-if="teams.length === 0" class="text-center text-muted py-5">
          <i class="bi bi-people display-1 d-block mb-3"></i>
          <h5>Команд пока нет</h5>
          <p class="mb-0">Добавьте первую команду используя форму выше</p>
        </div>
        
        <div v-else class="row g-4">
          <div v-for="team in teams" :key="team.id" class="col-12 col-md-6 col-lg-4 col-xl-3">
            <div class="team-card card h-100">
              <div class="card-body text-center">
                <!-- Логотип команды -->
                <div class="team-logo mb-3" style="width: 120px; height: 120px; margin: 0 auto;">
                  <img 
                    v-if="getImageUrl(team.logo)" 
                    :src="getImageUrl(team.logo)" 
                    :alt="team.name"
                    class="img-fluid rounded"
                    style="width: 100%; height: 100%; object-fit: cover;"
                    @error="handleImageError"
                  />
                  <div v-else class="placeholder-logo bg-light rounded d-flex align-items-center justify-content-center" style="width: 100%; height: 100%;">
                    <i class="bi bi-people-fill text-muted" style="font-size: 3rem;"></i>
                  </div>
                </div>
                
                <!-- Название команды -->
                <h5 class="card-title">{{ team.name }}</h5>
                
                <!-- Дата создания -->
                <p class="text-muted small">
                  <i class="bi bi-calendar me-1"></i>
                  {{ new Date(team.created_at).toLocaleDateString('ru-RU') }}
                </p>
              </div>
              
              <!-- Кнопки действий -->
              <div class="card-footer bg-transparent">
                <div class="d-flex gap-2 justify-content-center">
                  <button 
                    class="btn btn-outline-danger btn-sm" 
                    @click="onRemoveClick(team)"
                    :disabled="isLoading"
                    title="Удалить"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                  
                  <button
                    class="btn btn-outline-success btn-sm"
                    @click="onTeamEditClick(team)"
                    data-bs-toggle="modal"
                    data-bs-target="#editTeamModal"
                    :disabled="isLoading"
                    title="Редактировать"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Модальное окно редактирования -->
  <div class="modal fade" id="editTeamModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">
            <i class="bi bi-pencil-square me-2"></i>Редактировать команду
          </h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
            :disabled="isLoading"
          ></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <div class="form-floating">
              <input
                type="text"
                class="form-control"
                v-model="teamToEdit.name"
                placeholder="Название команды"
                :disabled="isLoading"
              />
              <label>Название команды</label>
            </div>
          </div>
          
          <!-- Текущее лого -->
          <div class="mb-3" v-if="teamToEdit.logo">
            <p class="text-muted mb-2">Текущее лого:</p>
            <div style="width: 150px; height: 150px; margin: 0 auto;">
              <img 
                v-if="getImageUrl(teamToEdit.logo)" 
                :src="getImageUrl(teamToEdit.logo)" 
                :alt="teamToEdit.name"
                class="img-thumbnail"
                style="width: 100%; height: 100%; object-fit: contain;"
                @error="handleImageError"
              />
              <div v-else class="placeholder-logo bg-light rounded d-flex align-items-center justify-content-center" style="width: 100%; height: 100%;">
                <i class="bi bi-people-fill text-muted" style="font-size: 2.5rem;"></i>
              </div>
            </div>
          </div>
          
          <!-- Загрузка нового лого -->
          <div class="mb-3">
            <div class="form-floating">
              <input
                type="file"
                class="form-control"
                ref="teamEditLogoRef"
                @change="teamEditLogoChange"
                accept="image/*"
                :disabled="isLoading"
              />
              <label>Новое лого (оставьте пустым, чтобы не менять)</label>
            </div>
          </div>
          
          <!-- Предпросмотр нового лого -->
          <div v-if="teamEditImageUrl" class="mt-3">
            <p class="text-muted mb-2">Предпросмотр нового лого:</p>
            <img 
              :src="teamEditImageUrl" 
              alt="Предпросмотр нового лого"
              class="img-thumbnail d-block mx-auto"
              style="max-width: 150px; max-height: 150px; object-fit: contain;"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
            :disabled="isLoading"
          >
            Отмена
          </button>
          <button
            data-bs-dismiss="modal"
            type="button"
            class="btn btn-primary"
            @click="onUpdateTeam"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
            <i class="bi bi-check-lg me-1"></i>Сохранить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.team-card {
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.team-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #007bff;
}

.placeholder-logo {
  border: 2px dashed #dee2e6;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
}

.card-header {
  border-bottom: 2px solid rgba(0,0,0,0.125);
}
</style>