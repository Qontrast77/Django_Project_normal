<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref } from 'vue';

const tournaments = ref([]);
const categories = ref([]);
const isLoading = ref(false);
const error = ref(null);

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
    
    // Просто закрываем модальное окно через data-bs-dismiss
    // Кнопка "Сохранить" уже имеет data-bs-dismiss="modal"
    
  } catch (err) {
    console.error('Ошибка обновления турнира:', err);
    error.value = err.response?.data || 'Не удалось обновить турнир';
  } finally {
    isLoading.value = false;
  }
}

// Функция для форматирования даты для input[type="date"]
function formatDateForInput(dateString) {
  if (!dateString) return '';
  try {
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
  } catch {
    return '';
  }
}

// Функция для форматирования даты для отображения
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
      <strong>Ошибка!</strong> {{ typeof error === 'object' ? JSON.stringify(error) : error }}
      <button type="button" class="btn-close" @click="error = null"></button>
    </div>

    <!-- Форма добавления турнира -->
    <div class="card mb-4">
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
          
          <!-- Информация о длительности -->
          <div v-if="tournamentToAdd.start_date && tournamentToAdd.end_date" class="mt-3">
            <small class="text-muted">
              Длительность: {{ getTournamentDuration(tournamentToAdd.start_date, tournamentToAdd.end_date) }} дней
            </small>
          </div>
        </form>
      </div>
    </div>

    <!-- Список турниров -->
    <div class="card">
      <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <h3 class="mb-0">Список турниров</h3>
        <span class="badge bg-primary">{{ tournaments.length }} турниров</span>
      </div>
      <div class="card-body">
        <div v-if="tournaments.length === 0" class="text-center text-muted py-5">
          <i class="bi bi-trophy display-1 d-block mb-3"></i>
          <h5>Турниров пока нет</h5>
          <p class="mb-0">Добавьте первый турнир используя форму выше</p>
        </div>
        
        <div v-else class="row g-4">
          <div v-for="tournament in tournaments" :key="tournament.id" class="col-12 col-md-6 col-lg-4 col-xl-3">
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
              
              <div class="card-footer bg-transparent">
                <div class="d-flex gap-2 justify-content-end">
                  <button 
                    class="btn btn-outline-danger btn-sm" 
                    @click="onRemoveClick(tournament)"
                    :disabled="isLoading"
                    title="Удалить"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                  
                  <button
                    class="btn btn-outline-success btn-sm"
                    @click="onTournamentEditClick(tournament)"
                    data-bs-toggle="modal"
                    data-bs-target="#editTournamentModal"
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
  <div class="modal fade" id="editTournamentModal" tabindex="-1">
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
              
              <!-- Информация о длительности -->
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

/* Адаптивность */
@media (max-width: 768px) {
  .tournament-card {
    margin-bottom: 1rem;
  }
}
</style>