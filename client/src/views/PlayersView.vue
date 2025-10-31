<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref, computed } from 'vue';
import { useUserStore } from '@/stores/user_store';
import { storeToRefs } from "pinia";

const userStore = useUserStore();
const { userInfo } = storeToRefs(userStore);

const players = ref([]);
const teams = ref([]);
const isLoading = ref(false);
const error = ref(null);

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

async function fetchPlayers() {
    try {
        isLoading.value = true;
        error.value = null;
        const response = await axios.get("/api/players/");
        players.value = response.data;
    } catch (err) {
        console.error('Ошибка загрузки игроков:', err);
        error.value = err.response?.data || 'Не удалось загрузить игроков';
        players.value = [];
    } finally {
        isLoading.value = false;
    }
}

async function fetchTeams() {
    try {
        const response = await axios.get("/api/teams/");
        teams.value = response.data;
    } catch (err) {
        console.error('Ошибка загрузки команд:', err);
        teams.value = [];
    }
}

onBeforeMount(async () => {
    await fetchPlayers();
    await fetchTeams();
})

const playerToAdd = ref({
    name: '',
    nickname: '',
    team: null
});
const playerPhotoRef = ref();
const playerImageUrl = ref();

function playerPhotoChange() {
  if (playerPhotoRef.value.files[0]) {
    playerImageUrl.value = URL.createObjectURL(playerPhotoRef.value.files[0]);
  }
}

async function onPlayerAdd() {
  try {
    isLoading.value = true;
    error.value = null;
    
    const formData = new FormData();
    formData.append('name', playerToAdd.value.name || '');
    formData.append('nickname', playerToAdd.value.nickname || '');
    
    if (playerToAdd.value.team && playerToAdd.value.team !== 'null') {
        const teamId = parseInt(playerToAdd.value.team);
        if (!isNaN(teamId)) {
            formData.append('team', teamId.toString());
        }
    } else {
        formData.append('team', '');
    }
    
    if (playerPhotoRef.value.files[0]) {
      formData.append('photo', playerPhotoRef.value.files[0]);
    }
    
    await axios.post("/api/players/", formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    await fetchPlayers();
    
    playerToAdd.value = {
        name: '',
        nickname: '',
        team: null
    };
    playerImageUrl.value = null;
    if (playerPhotoRef.value) {
      playerPhotoRef.value.value = '';
    }
  } catch (err) {
    console.error('Ошибка добавления игрока:', err);
    error.value = err.response?.data || 'Не удалось добавить игрока';
  } finally {
    isLoading.value = false;
  }
}

async function onRemoveClick(player) {
  if (!confirm(`Удалить игрока "${player.name}"?`)) return;
  
  try {
    await axios.delete(`/api/players/${player.id}/`);
    await fetchPlayers();
  } catch (err) {
    console.error('Ошибка удаления игрока:', err);
    error.value = err.response?.data || 'Не удалось удалить игрока';
  }
}

const playerToEdit = ref({});
const playerEditPhotoRef = ref();
const playerEditImageUrl = ref();

function playerEditPhotoChange() {
  if (playerEditPhotoRef.value.files[0]) {
    playerEditImageUrl.value = URL.createObjectURL(playerEditPhotoRef.value.files[0]);
  }
}

function onPlayerEditClick(player) {
  playerToEdit.value = { 
    ...player,
    team: player.team?.id || player.team || null
  };
  playerEditImageUrl.value = null;
}

async function onUpdatePlayer() {
  try {
    isLoading.value = true;
    error.value = null;
    
    const formData = new FormData();
    formData.append('name', playerToEdit.value.name || '');
    formData.append('nickname', playerToEdit.value.nickname || '');
    
    if (playerToEdit.value.team && playerToEdit.value.team !== 'null') {
        const teamId = parseInt(playerToEdit.value.team);
        if (!isNaN(teamId)) {
            formData.append('team', teamId.toString());
        }
    } else {
        formData.append('team', '');
    }
    
    if (playerEditPhotoRef.value.files[0]) {
      formData.append('photo', playerEditPhotoRef.value.files[0]);
    }
    
    await axios.put(`/api/players/${playerToEdit.value.id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    await fetchPlayers();
    
  } catch (err) {
    console.error('Ошибка обновления игрока:', err);
    error.value = err.response?.data || 'Не удалось обновить игрока';
  } finally {
    isLoading.value = false;
  }
}

// Функция для получения URL изображения с timestamp (как в TeamsView)
function getImageUrl(imagePath) {
  if (!imagePath) return null;
  
  if (imagePath.startsWith('http') || imagePath.startsWith('data:')) {
    return imagePath;
  }
  
  let url = imagePath.startsWith('/') ? imagePath : `/${imagePath}`;
  
  // Добавляем timestamp для предотвращения кэширования (как в TeamsView)
  const timestamp = Date.now();
  if (url.includes('?')) {
    url += `&t=${timestamp}`;
  } else {
    url += `?t=${timestamp}`;
  }
  
  return url;
}

// Обработчик ошибок изображений (как в TeamsView)
function handleImageError(event) {
  console.log('Изображение не загружено:', event.target.src);
  event.target.style.display = 'none';
  event.target.onerror = null;
}

function getTeamName(teamId) {
  if (!teamId) return 'Без команды';
  if (typeof teamId === 'object') return teamId.name;
  const team = teams.value.find(t => t.id === teamId);
  return team ? team.name : 'Команда не найдена';
}

// Проверка прав доступа
const canEditPlayers = computed(() => {
  return userInfo.value && userInfo.value.is_authenticated && userInfo.value.is_staff;
});
</script>

<template>
  <div class="container-fluid pt-5">
    <!-- Состояния загрузки и ошибок -->
    <div v-if="isLoading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
      <p class="mt-2 text-muted">Загрузка...</p>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>Ошибка!</strong> {{ typeof error === 'object' ? JSON.stringify(error) : error }}
      <button type="button" class="btn-close" @click="error = null"></button>
    </div>

    <!-- Форма добавления игрока (только для админов) -->
    <div v-if="canEditPlayers" class="card mb-4">
      <div class="card-header bg-primary text-white">
        <h3 class="mb-0">Добавить игрока</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent.stop="onPlayerAdd" enctype="multipart/form-data">
          <div class="row g-3">
            <div class="col-md-3">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="playerToAdd.name"
                  placeholder="Имя игрока"
                  required
                  :disabled="isLoading"
                />
                <label>Имя игрока</label>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="playerToAdd.nickname"
                  placeholder="Никнейм"
                  required
                  :disabled="isLoading"
                />
                <label>Никнейм</label>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-floating">
                <select class="form-select" v-model="playerToAdd.team" :disabled="isLoading">
                  <option :value="null">Без команды</option>
                  <option :value="team.id" v-for="team in teams" :key="team.id">
                    {{ team.name }}
                  </option>
                </select>
                <label>Команда</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input
                  type="file"
                  class="form-control"
                  ref="playerPhotoRef"
                  @change="playerPhotoChange"
                  accept="image/*"
                  :disabled="isLoading"
                />
                <label>Фото игрока</label>
              </div>
            </div>
            <div class="col-md-1">
              <button type="submit" class="btn btn-primary h-100 w-100" :disabled="isLoading">
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                Добавить
              </button>
            </div>
          </div>
          
          <!-- Предпросмотр изображения -->
          <div v-if="playerImageUrl" class="mt-3">
            <p class="text-muted mb-2">Предпросмотр:</p>
            <img 
              :src="playerImageUrl" 
              alt="Предпросмотр фото"
              class="img-thumbnail rounded-circle"
              style="max-width: 200px; max-height: 200px; object-fit: cover;"
            />
          </div>
        </form>
      </div>
    </div>

    <!-- Список игроков -->
    <div class="card">
      <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <h3 class="mb-0">Список игроков</h3>
        <span class="badge bg-primary">{{ players.length }} игроков</span>
      </div>
      <div class="card-body">
        <div v-if="players.length === 0" class="text-center text-muted py-5">
          <i class="bi bi-people display-1 d-block mb-3"></i>
          <h5>Игроков пока нет</h5>
          <p class="mb-0">Добавьте первого игрока используя форму выше</p>
        </div>
        
        <div v-else class="row g-4">
          <div v-for="player in players" :key="player.id" class="col-12 col-md-6 col-lg-4 col-xl-3">
            <div class="player-card card h-100">
              <div class="card-body text-center">
                <!-- Фото игрока -->
                <div class="player-photo mb-3" style="width: 120px; height: 120px; margin: 0 auto;">
                  <img 
                    v-if="getImageUrl(player.photo)" 
                    :src="getImageUrl(player.photo)" 
                    :alt="player.name"
                    class="img-fluid rounded-circle"
                    style="width: 100%; height: 100%; object-fit: cover;"
                    @error="handleImageError"
                    :key="player.id + (player.photo ? player.photo : '')"
                  />
                  <div v-else class="placeholder-photo bg-light rounded-circle d-flex align-items-center justify-content-center" style="width: 100%; height: 100%;">
                    <i class="bi bi-person-fill text-muted" style="font-size: 3rem;"></i>
                  </div>
                </div>
                
                <!-- Информация об игроке -->
                <h5 class="card-title">{{ player.name }}</h5>
                <p class="text-primary mb-1">
                  <strong>{{ player.nickname }}</strong>
                </p>
                <p class="text-muted small mb-0">
                  <i class="bi bi-people me-1"></i>
                  {{ getTeamName(player.team) }}
                </p>
              </div>
              
              <!-- Кнопки действий (только для админов) -->
              <div v-if="canEditPlayers" class="card-footer bg-transparent">
                <div class="d-flex gap-2 justify-content-center">
                  <button 
                    class="btn btn-outline-danger btn-sm" 
                    @click="onRemoveClick(player)"
                    :disabled="isLoading"
                    title="Удалить"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                  
                  <button
                    class="btn btn-outline-success btn-sm"
                    @click="onPlayerEditClick(player)"
                    data-bs-toggle="modal"
                    data-bs-target="#editPlayerModal"
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

  <!-- Модальное окно редактирования (только для админов) -->
  <div v-if="canEditPlayers" class="modal fade" id="editPlayerModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">
            <i class="bi bi-pencil-square me-2"></i>Редактировать игрока
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
          <form @submit.prevent.stop="onUpdatePlayer" enctype="multipart/form-data">
            <div class="row g-3">
              <div class="col-6">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="playerToEdit.name"
                    placeholder="Имя игрока"
                    :disabled="isLoading"
                  />
                  <label>Имя игрока</label>
                </div>
              </div>
              <div class="col-6">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="playerToEdit.nickname"
                    placeholder="Никнейм"
                    :disabled="isLoading"
                  />
                  <label>Никнейм</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <select class="form-select" v-model="playerToEdit.team" :disabled="isLoading">
                    <option :value="null">Без команды</option>
                    <option :value="team.id" v-for="team in teams" :key="team.id">
                      {{ team.name }}
                    </option>
                  </select>
                  <label>Команда</label>
                </div>
              </div>
              
              <!-- Текущее фото -->
              <div class="col-12" v-if="playerToEdit.photo">
                <p class="text-muted mb-2">Текущее фото:</p>
                <div style="width: 150px; height: 150px; margin: 0 auto;">
                  <img 
                    v-if="getImageUrl(playerToEdit.photo)" 
                    :src="getImageUrl(playerToEdit.photo)" 
                    :alt="playerToEdit.name"
                    class="img-thumbnail rounded-circle"
                    style="width: 100%; height: 100%; object-fit: cover;"
                    @error="handleImageError"
                  />
                  <div v-else class="placeholder-photo bg-light rounded-circle d-flex align-items-center justify-content-center" style="width: 100%; height: 100%;">
                    <i class="bi bi-person-fill text-muted" style="font-size: 2.5rem;"></i>
                  </div>
                </div>
              </div>
              
              <!-- Загрузка нового фото -->
              <div class="col-12">
                <div class="form-floating">
                  <input
                    type="file"
                    class="form-control"
                    ref="playerEditPhotoRef"
                    @change="playerEditPhotoChange"
                    accept="image/*"
                    :disabled="isLoading"
                  />
                  <label>Новое фото (оставьте пустым, чтобы не менять)</label>
                </div>
              </div>
              
              <!-- Предпросмотр нового фото -->
              <div class="col-12" v-if="playerEditImageUrl">
                <p class="text-muted mb-2">Предпросмотр нового фото:</p>
                <img 
                  :src="playerEditImageUrl" 
                  alt="Предпросмотр нового фото"
                  class="img-thumbnail rounded-circle d-block mx-auto"
                  style="max-width: 150px; max-height: 150px; object-fit: cover;"
                />
              </div>
            </div>
          </form>
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
            @click="onUpdatePlayer"
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
.player-card {
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.player-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #007bff;
}

.player-photo img,
.placeholder-photo {
  transition: transform 0.3s ease;
}

.player-card:hover .player-photo img,
.player-card:hover .placeholder-photo {
  transform: scale(1.05);
}

.placeholder-photo {
  border: 2px dashed #dee2e6;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
}

.card-header {
  border-bottom: 2px solid rgba(0,0,0,0.125);
}

@media (max-width: 768px) {
  .player-photo {
    width: 100px !important;
    height: 100px !important;
  }
  
  .placeholder-photo i {
    font-size: 2.5rem !important;
  }
}
</style>