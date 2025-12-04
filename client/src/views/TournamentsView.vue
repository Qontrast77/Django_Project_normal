<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref, computed } from 'vue';
import { useUserStore } from '@/stores/user_store';
import { storeToRefs } from "pinia";

const userStore = useUserStore();
const { userInfo } = storeToRefs(userStore);

const tournaments = ref([]);
const categories = ref([]);
const isLoading = ref(false);
const error = ref(null);
const selectedCategoryFilter = ref('all'); // Фильтр по категории

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

async function fetchTournaments() {
    try {
        isLoading.value = true;
        error.value = null;
        const response = await axios.get("/api/tournaments/");
        tournaments.value = response.data;
    } catch (err) {
        console.error('Ошибка загрузки турниров:', err);
        error.value = err.response?.data || 'Не удалось загрузить турниры';
        tournaments.value = [];
    } finally {
        isLoading.value = false;
    }
}

async function fetchCategories() {
    try {
        const response = await axios.get("/api/tournament-categories/");
        categories.value = response.data;
    } catch (err) {
        console.error('Ошибка загрузки категорий:', err);
        categories.value = [];
    }
}

onBeforeMount(async () => {
    await fetchTournaments();
    await fetchCategories();
})

// Вычисляемое свойство для отфильтрованных турниров
const filteredTournaments = computed(() => {
    if (selectedCategoryFilter.value === 'all') {
        return tournaments.value;
    }
    
    const categoryId = parseInt(selectedCategoryFilter.value);
    return tournaments.value.filter(tournament => {
        const tournamentCategoryId = tournament.category?.id || tournament.category;
        return tournamentCategoryId === categoryId;
    });
});

// Функция сброса фильтра
function resetFilter() {
    selectedCategoryFilter.value = 'all';
}

const tournamentToAdd = ref({
    name: '',
    category: null,
    start_date: '',
    end_date: ''
});

async function onTournamentAdd() {
  try {
    isLoading.value = true;
    error.value = null;
    
    // Проверяем обязательные поля
    if (!tournamentToAdd.value.name.trim()) {
      error.value = 'Название турнира обязательно для заполнения';
      return;
    }

    if (!tournamentToAdd.value.start_date || !tournamentToAdd.value.end_date) {
      error.value = 'Дата начала и окончания обязательны';
      return;
    }

    // Проверяем, что дата окончания не раньше даты начала
    if (new Date(tournamentToAdd.value.end_date) < new Date(tournamentToAdd.value.start_date)) {
      error.value = 'Дата окончания не может быть раньше даты начала';
      return;
    }

    const data = {
      name: tournamentToAdd.value.name.trim(),
      category: tournamentToAdd.value.category && tournamentToAdd.value.category !== 'null' ? parseInt(tournamentToAdd.value.category) : null,
      start_date: tournamentToAdd.value.start_date,
      end_date: tournamentToAdd.value.end_date
    };

    console.log('Добавление турнира:', data);

    await axios.post("/api/tournaments/", data);
    await fetchTournaments();
    
    // Сброс формы
    tournamentToAdd.value = {
        name: '',
        category: null,
        start_date: '',
        end_date: ''
    };
  } catch (err) {
    console.error('Ошибка добавления турнира:', err);
    error.value = err.response?.data || 'Не удалось добавить турнир';
  } finally {
    isLoading.value = false;
  }
}

async function onRemoveClick(tournament) {
  if (!confirm(`Удалить турнир "${tournament.name}"?`)) return;
  
  try {
    await axios.delete(`/api/tournaments/${tournament.id}/`);
    await fetchTournaments();
  } catch (err) {
    console.error('Ошибка удаления турнира:', err);
    error.value = err.response?.data || 'Не удалось удалить турнир';
  }
}

const tournamentToEdit = ref({
    name: '',
    category: null,
    start_date: '',
    end_date: ''
});

function onTournamentEditClick(tournament) {
  tournamentToEdit.value = { 
    ...tournament,
    name: tournament.name || '',
    category: tournament.category?.id || tournament.category || null,
    start_date: tournament.start_date ? formatDateForInput(tournament.start_date) : '',
    end_date: tournament.end_date ? formatDateForInput(tournament.end_date) : ''
  };
}

async function onUpdateTournament() {
  try {
    isLoading.value = true;
    error.value = null;
    
    // Проверяем обязательные поля
    if (!tournamentToEdit.value.name.trim()) {
      error.value = 'Название турнира обязательно для заполнения';
      return;
    }

    if (!tournamentToEdit.value.start_date || !tournamentToEdit.value.end_date) {
      error.value = 'Дата начала и окончания обязательны';
      return;
    }

    // Проверяем, что дата окончания не раньше даты начала
    if (new Date(tournamentToEdit.value.end_date) < new Date(tournamentToEdit.value.start_date)) {
      error.value = 'Дата окончания не может быть раньше даты начала';
      return;
    }

    const data = {
      name: tournamentToEdit.value.name.trim(),
      category: tournamentToEdit.value.category && tournamentToEdit.value.category !== 'null' ? parseInt(tournamentToEdit.value.category) : null,
      start_date: tournamentToEdit.value.start_date,
      end_date: tournamentToEdit.value.end_date
    };

    console.log('Обновление турнира:', tournamentToEdit.value.id, data);

    const response = await axios.put(`/api/tournaments/${tournamentToEdit.value.id}/`, data);
    console.log('Ответ сервера:', response.data);
    
    await fetchTournaments();
    
  } catch (err) {
    console.error('Ошибка обновления турнира:', err);
    error.value = err.response?.data || 'Не удалось обновить турнир';
  } finally {
    isLoading.value = false;
  }
}


function formatDateForInput(dateString) {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
  } catch {
    return '';
  }
}


function formatDisplayDate(dateString) {
  if (!dateString) return 'Не указана';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
  } catch {
    return 'Неверная дата';
  }
}

// Функция для получения названия категории
function getCategoryName(categoryId) {
  if (!categoryId) return 'Без категории';
  if (typeof categoryId === 'object') return categoryId.name;
  const category = categories.value.find(c => c.id === categoryId);
  return category ? category.name : 'Категория не найдена';
}

// Функция для расчета длительности турнира в днях
function getTournamentDuration(startDate, endDate) {
  if (!startDate || !endDate) return 0;
  try {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    return diffDays;
  } catch {
    return 0;
  }
}

// Проверка прав доступа
const canEditTournaments = computed(() => {
  return userInfo.value && userInfo.value.is_authenticated && userInfo.value.is_staff;
});
</script>

<template class="content">
  <div class="container pt-5">
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

    <!-- Форма добавления турнира (только для админов) -->
    <div v-if="canEditTournaments" class="card mb-4">
      <div class="card-header bg-primary text-white">
        <h3 class="mb-0">Добавить турнир</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent.stop="onTournamentAdd">
          <div class="row g-3">
            <div class="col-md-4">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="tournamentToAdd.name"
                  placeholder="Название турнира"
                  required
                  :disabled="isLoading"
                />
                <label>Название турнира</label>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-floating">
                <select class="form-select" v-model="tournamentToAdd.category" :disabled="isLoading">
                  <option :value="null">Без категории</option>
                  <option :value="category.id" v-for="category in categories" :key="category.id">
                    {{ category.name }}
                  </option>
                </select>
                <label>Категория</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input
                  type="date"
                  class="form-control"
                  v-model="tournamentToAdd.start_date"
                  required
                  :disabled="isLoading"
                />
                <label>Дата начала</label>
              </div>
            </div>
            <div class="col-md-2">
              <div class="form-floating">
                <input
                  type="date"
                  class="form-control"
                  v-model="tournamentToAdd.end_date"
                  required
                  :disabled="isLoading"
                />
                <label>Дата окончания</label>
              </div>
            </div>
            <div class="col-md-1">
              <button type="submit" class="btn btn-primary h-100 w-100" :disabled="isLoading">
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                Добавить
              </button>
            </div>
          </div>
          
          
          <div v-if="tournamentToAdd.start_date && tournamentToAdd.end_date" class="mt-3">
            <small class="text-muted">
              Длительность: {{ getTournamentDuration(tournamentToAdd.start_date, tournamentToAdd.end_date) }} дней
            </small>
          </div>
        </form>
      </div>
    </div>

    
    <div class="card mb-4">
      <div class="card-header bg-info text-white">
        <h3 class="mb-0">
          <i class="bi bi-funnel me-2"></i>Фильтр по категориям
        </h3>
      </div>
      <div class="card-body">
        <div class="row align-items-center">
          <div class="col-md-6">
            <label class="form-label fw-bold">Выберите категорию для фильтрации турниров:</label>
            <select class="form-select" v-model="selectedCategoryFilter">
              <option value="all">🏷️ Все категории</option>
              <option 
                v-for="category in categories" 
                :key="category.id" 
                :value="category.id"
              >
                {{ category.name }}
              </option>
            </select>
          </div>
          <div class="col-md-6">
            <div v-if="selectedCategoryFilter !== 'all'" class="alert alert-info mt-3">
              <i class="bi bi-info-circle me-2"></i>
              <strong>Фильтр активен:</strong> 
              Показываются турниры категории 
              <strong class="text-primary">
                {{ categories.find(c => c.id === parseInt(selectedCategoryFilter))?.name }}
              </strong>
              <button class="btn btn-sm btn-outline-info ms-2" @click="resetFilter">
                <i class="bi bi-x me-1"></i>Сбросить
              </button>
            </div>
            <div v-else class="text-muted mt-3">
              <i class="bi bi-info-circle me-2"></i>
              Выберите категорию для фильтрации турниров
            </div>
          </div>
        </div>
      </div>
    </div>

    
    <div class="card">
      <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <h3 class="mb-0">Список турниров</h3>
        <span class="badge bg-primary">{{ filteredTournaments.length }} турниров</span>
      </div>
      <div class="card-body">
        <div v-if="filteredTournaments.length === 0" class="text-center text-muted py-5">
          <i class="bi bi-trophy display-1 d-block mb-3"></i>
          <h5>Турниров пока нет</h5>
          <p class="mb-0" v-if="selectedCategoryFilter !== 'all'">
            В выбранной категории пока нет турниров
          </p>
          <p class="mb-0" v-else>
            Добавьте первый турнир используя форму выше
          </p>
        </div>
        
        <div v-else class="row g-4">
          <div v-for="tournament in filteredTournaments" :key="tournament.id" class="col-12 col-md-6 col-lg-4 col-xl-3">
            <div class="tournament-card card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <h5 class="card-title mb-0">{{ tournament.name }}</h5>
                  <span class="badge bg-info">ID: {{ tournament.id }}</span>
                </div>
                
                <div class="tournament-info">
                  <p class="mb-2">
                    <i class="bi bi-tag me-2 text-muted"></i>
                    <strong>Категория:</strong> {{ getCategoryName(tournament.category) }}
                  </p>
                  
                  <p class="mb-2">
                    <i class="bi bi-calendar-event me-2 text-muted"></i>
                    <strong>Начало:</strong> {{ formatDisplayDate(tournament.start_date) }}
                  </p>
                  
                  <p class="mb-2">
                    <i class="bi bi-calendar-check me-2 text-muted"></i>
                    <strong>Окончание:</strong> {{ formatDisplayDate(tournament.end_date) }}
                  </p>
                  
                  <p class="mb-0">
                    <i class="bi bi-clock me-2 text-muted"></i>
                    <strong>Длительность:</strong> 
                    {{ getTournamentDuration(tournament.start_date, tournament.end_date) }} дней
                  </p>
                </div>
              </div>
              
              <!-- Кнопки действий (только для админов) -->
              <div v-if="canEditTournaments" class="card-footer bg-transparent">
                <div class="d-flex gap-2 justify-content-end">
                  <button 
                    class="btn btn-outline-danger btn-sm" 
                    @click="onRemoveClick(tournament)"
                    :disabled="isLoading"
                    title="Удалить"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">
  <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/>
</svg>
                  </button>
                  
                  <button
                    class="btn btn-outline-success btn-sm"
                    @click="onTournamentEditClick(tournament)"
                    data-bs-toggle="modal"
                    data-bs-target="#editTournamentModal"
                    :disabled="isLoading"
                    title="Редактировать"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16">
  <path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325"/>
</svg>
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
  <div v-if="canEditTournaments" class="modal fade" id="editTournamentModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">
            <i class="bi bi-pencil-square me-2"></i>Редактировать турнир
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
          <form @submit.prevent.stop="onUpdateTournament">
            <div class="row g-3">
              <div class="col-12">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="tournamentToEdit.name"
                    placeholder="Название турнира"
                    required
                    :disabled="isLoading"
                  />
                  <label>Название турнира</label>
                </div>
              </div>
              
              <div class="col-12">
                <div class="form-floating">
                  <select class="form-select" v-model="tournamentToEdit.category" :disabled="isLoading">
                    <option :value="null">Без категории</option>
                    <option :value="category.id" v-for="category in categories" :key="category.id">
                      {{ category.name }}
                    </option>
                  </select>
                  <label>Категория</label>
                </div>
              </div>
              
              <div class="col-6">
                <div class="form-floating">
                  <input
                    type="date"
                    class="form-control"
                    v-model="tournamentToEdit.start_date"
                    required
                    :disabled="isLoading"
                  />
                  <label>Дата начала</label>
                </div>
              </div>
              
              <div class="col-6">
                <div class="form-floating">
                  <input
                    type="date"
                    class="form-control"
                    v-model="tournamentToEdit.end_date"
                    required
                    :disabled="isLoading"
                  />
                  <label>Дата окончания</label>
                </div>
              </div>
              
              
              <div class="col-12" v-if="tournamentToEdit.start_date && tournamentToEdit.end_date">
                <div class="alert alert-info py-2">
                  <small>
                    <i class="bi bi-info-circle me-1"></i>
                    Длительность турнира: {{ getTournamentDuration(tournamentToEdit.start_date, tournamentToEdit.end_date) }} дней
                  </small>
                </div>
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
            type="button"
            class="btn btn-primary"
            @click="onUpdateTournament"
            data-bs-dismiss="modal"
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
.tournament-card {
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.tournament-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #007bff;
}

.card-title {
  color: #2c3e50;
  font-weight: 600;
}

.tournament-info {
  font-size: 0.9rem;
}

.tournament-info p {
  margin-bottom: 0.5rem;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
}

.card-header {
  border-bottom: 2px solid rgba(0,0,0,0.125);
}

</style>