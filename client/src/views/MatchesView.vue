<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref } from 'vue';

const matches = ref([]);
const tournaments = ref([]);
const teams = ref([]);
const isLoading = ref(false);
const error = ref(null);

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

async function fetchMatches() {
    try {
        isLoading.value = true;
        error.value = null;
        const response = await axios.get("/api/matches/");
        matches.value = response.data;
    } catch (error) {
        console.error('Ошибка при загрузке матчей:', error);
        matches.value = [];
    } finally {
        isLoading.value = false;
    }
}

async function fetchTournaments() {
    try {
        const response = await axios.get("/api/tournaments/");
        tournaments.value = response.data;
    } catch (error) {
        console.error('Ошибка при загрузке турниров:', error);
        tournaments.value = [];
    }
}

async function fetchTeams() {
    try {
        const response = await axios.get("/api/teams/");
        teams.value = response.data;
    } catch (error) {
        console.error('Ошибка при загрузке команд:', error);
        teams.value = [];
    }
}

onBeforeMount(async () => {
    await fetchMatches();
    await fetchTournaments();
    await fetchTeams();
})

const matchToAdd = ref({
    team1_score: 0,
    team2_score: 0,
    tournament: null,
    team1: null,
    team2: null,
    match_date: ''
});

async function onMatchAdd() {
    try {
        isLoading.value = true;
        error.value = null;
        
        // Подготавливаем данные для отправки
        const data = {
            tournament: matchToAdd.value.tournament && matchToAdd.value.tournament !== 'null' ? parseInt(matchToAdd.value.tournament) : null,
            team1: matchToAdd.value.team1 && matchToAdd.value.team1 !== 'null' ? parseInt(matchToAdd.value.team1) : null,
            team2: matchToAdd.value.team2 && matchToAdd.value.team2 !== 'null' ? parseInt(matchToAdd.value.team2) : null,
            match_date: matchToAdd.value.match_date,
            team1_score: parseInt(matchToAdd.value.team1_score) || 0,
            team2_score: parseInt(matchToAdd.value.team2_score) || 0
        };

        console.log('Отправка данных матча:', data);

        await axios.post("/api/matches/", data);
        await fetchMatches();
        
        // Сброс формы
        matchToAdd.value = {
            team1_score: 0,
            team2_score: 0,
            tournament: null,
            team1: null,
            team2: null,
            match_date: ''
        };
    } catch (err) {
        console.error('Ошибка при добавлении матча:', err);
        error.value = err.response?.data || 'Не удалось добавить матч';
    } finally {
        isLoading.value = false;
    }
}

async function onRemoveClick(match) {
    if (confirm('Вы уверены, что хотите удалить этот матч?')) {
        try {
            await axios.delete(`/api/matches/${match.id}/`);
            await fetchMatches();
        } catch (error) {
            console.error('Ошибка при удалении матча:', error);
            alert('Ошибка при удалении матча');
        }
    }
}

const matchToEdit = ref({});

async function onMatchEditClick(match) {
    matchToEdit.value = { 
        ...match,
        tournament: match.tournament?.id || match.tournament || null,
        team1: match.team1?.id || match.team1 || null,
        team2: match.team2?.id || match.team2 || null,
        winner: match.winner?.id || match.winner || null,
        match_date: match.match_date ? match.match_date.slice(0, 16) : ''
    };
}

async function onUpdateMatch() {
    try {
        isLoading.value = true;
        error.value = null;
        
        // Подготавливаем данные для обновления
        const data = {
            tournament: matchToEdit.value.tournament && matchToEdit.value.tournament !== 'null' ? parseInt(matchToEdit.value.tournament) : null,
            team1: matchToEdit.value.team1 && matchToEdit.value.team1 !== 'null' ? parseInt(matchToEdit.value.team1) : null,
            team2: matchToEdit.value.team2 && matchToEdit.value.team2 !== 'null' ? parseInt(matchToEdit.value.team2) : null,
            match_date: matchToEdit.value.match_date,
            team1_score: parseInt(matchToEdit.value.team1_score) || 0,
            team2_score: parseInt(matchToEdit.value.team2_score) || 0
        };

        console.log('Обновление матча:', matchToEdit.value.id, data);

        const response = await axios.put(`/api/matches/${matchToEdit.value.id}/`, data);
        console.log('Ответ сервера:', response.data);
        
        await fetchMatches();
    } catch (err) {
        console.error('Ошибка при обновлении матча:', err);
        error.value = err.response?.data || 'Не удалось обновить матч';
    } finally {
        isLoading.value = false;
    }
}

// Функция для получения названия команды по ID
function getTeamName(teamId) {
    if (!teamId) return 'Не указана';
    if (typeof teamId === 'object') {
        return teamId.name || 'Команда не найдена';
    }
    const team = teams.value.find(t => t.id === teamId);
    return team ? team.name : 'Команда не найдена';
}

// Функция для получения названия турнира по ID
function getTournamentName(tournamentId) {
    if (!tournamentId) return 'Без турнира';
    if (typeof tournamentId === 'object') {
        return tournamentId.name || 'Турнир не найден';
    }
    const tournament = tournaments.value.find(t => t.id === tournamentId);
    return tournament ? tournament.name : 'Турнир не найден';
}

// Функция для получения названия победителя
function getWinnerName(match) {
    if (!match.winner) return 'Ничья';
    
    if (typeof match.winner === 'object') {
        return match.winner.name;
    }
    
    const winnerTeam = teams.value.find(t => t.id === match.winner);
    return winnerTeam ? winnerTeam.name : 'Не определен';
}

// Функция для форматирования даты и времени
function formatDateTime(dateTimeString) {
    if (!dateTimeString) return 'Не указана';
    try {
        const date = new Date(dateTimeString);
        return date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return 'Неверная дата';
    }
}

// Функция для определения класса победителя
function getWinnerClass(match, teamId) {
    if (!match.winner) return '';
    
    let winnerId;
    if (typeof match.winner === 'object') {
        winnerId = match.winner.id;
    } else {
        winnerId = match.winner;
    }
    
    const compareId = typeof teamId === 'object' ? teamId.id : teamId;
    return winnerId === compareId ? 'winner-team' : '';
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

    <!-- Форма добавления матча -->
    <div class="card mb-4">
      <div class="card-header bg-primary text-white">
        <h3 class="mb-0">Добавить матч</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent.stop="onMatchAdd">
          <div class="row g-3">
            <div class="col-md-3">
              <div class="form-floating">
                <select class="form-select" v-model="matchToAdd.tournament" :disabled="isLoading">
                  <option :value="null">Без турнира</option>
                  <option :value="tournament.id" v-for="tournament in tournaments" :key="tournament.id">
                    {{ tournament.name }}
                  </option>
                </select>
                <label>Турнир</label>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-floating">
                <select class="form-select" v-model="matchToAdd.team1" required :disabled="isLoading">
                  <option :value="null">Выберите команду</option>
                  <option :value="team.id" v-for="team in teams" :key="team.id">
                    {{ team.name }}
                  </option>
                </select>
                <label>Команда 1</label>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-floating">
                <select class="form-select" v-model="matchToAdd.team2" required :disabled="isLoading">
                  <option :value="null">Выберите команду</option>
                  <option :value="team.id" v-for="team in teams" :key="team.id">
                    {{ team.name }}
                  </option>
                </select>
                <label>Команда 2</label>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-floating">
                <input
                  type="datetime-local"
                  class="form-control"
                  v-model="matchToAdd.match_date"
                  required
                  :disabled="isLoading"
                />
                <label>Дата и время матча</label>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-floating">
                <input
                  type="number"
                  class="form-control"
                  v-model="matchToAdd.team1_score"
                  placeholder="0"
                  min="0"
                  required
                  :disabled="isLoading"
                />
                <label>Счёт команды 1</label>
              </div>
            </div>
            <div class="col-md-3">
              <div class="form-floating">
                <input
                  type="number"
                  class="form-control"
                  v-model="matchToAdd.team2_score"
                  placeholder="0"
                  min="0"
                  required
                  :disabled="isLoading"
                />
                <label>Счёт команды 2</label>
              </div>
            </div>
            <div class="col-12">
              <button type="submit" class="btn btn-primary px-4" :disabled="isLoading">
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                <i class="bi bi-plus-circle me-2"></i>Добавить матч
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Список матчей -->
    <div class="card">
      <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <h3 class="mb-0">Список матчей</h3>
        <span class="badge bg-primary">{{ matches.length }} матчей</span>
      </div>
      <div class="card-body">
        <div v-if="matches.length === 0" class="text-center text-muted py-5">
          <i class="bi bi-emoji-frown display-1 d-block mb-3"></i>
          <h5>Матчей пока нет</h5>
          <p class="mb-0">Добавьте первый матч используя форму выше</p>
        </div>
        
        <div v-else class="row g-4">
          <div v-for="match in matches" :key="match.id" class="col-12 col-md-6 col-lg-4">
            <div class="match-card card h-100">
              <div class="card-header bg-light">
                <div class="d-flex justify-content-between align-items-center">
                  <small class="text-muted">
                    <i class="bi bi-trophy me-1"></i>
                    {{ getTournamentName(match.tournament) }}
                  </small>
                  <small class="text-muted">
                    <i class="bi bi-calendar me-1"></i>
                    {{ formatDateTime(match.match_date) }}
                  </small>
                </div>
              </div>
              
              <div class="card-body">
                <!-- Команда 1 -->
                <div class="team-row d-flex align-items-center justify-content-between mb-3">
                  <div class="team-info d-flex align-items-center">
                    <div class="team-logo me-2">
                      <i class="bi bi-flag-fill text-primary"></i>
                    </div>
                    <span :class="['team-name', getWinnerClass(match, match.team1?.id || match.team1)]">
                      {{ getTeamName(match.team1) }}
                    </span>
                  </div>
                  <div class="score">
                    <span class="badge bg-primary fs-6">{{ match.team1_score }}</span>
                  </div>
                </div>

                <!-- VS разделитель -->
                <div class="vs-divider text-center my-2">
                  <span class="badge bg-secondary">VS</span>
                </div>

                <!-- Команда 2 -->
                <div class="team-row d-flex align-items-center justify-content-between mb-3">
                  <div class="team-info d-flex align-items-center">
                    <div class="team-logo me-2">
                      <i class="bi bi-flag-fill text-danger"></i>
                    </div>
                    <span :class="['team-name', getWinnerClass(match, match.team2?.id || match.team2)]">
                      {{ getTeamName(match.team2) }}
                    </span>
                  </div>
                  <div class="score">
                    <span class="badge bg-primary fs-6">{{ match.team2_score }}</span>
                  </div>
                </div>

                <!-- Победитель -->
                <div v-if="match.winner" class="winner-section text-center mt-3 p-2 bg-success bg-opacity-10 rounded">
                  <small class="text-success">
                    <i class="bi bi-trophy-fill me-1"></i>
                    Победитель: <strong>{{ getWinnerName(match) }}</strong>
                  </small>
                </div>
                <div v-else class="winner-section text-center mt-3 p-2 bg-warning bg-opacity-10 rounded">
                  <small class="text-warning">
                    <i class="bi bi-arrow-left-right me-1"></i>
                    Ничья
                  </small>
                </div>
              </div>
              
              <div class="card-footer bg-transparent">
                <div class="d-flex gap-2 justify-content-end">
                  <button 
                    class="btn btn-outline-danger btn-sm" 
                    @click="onRemoveClick(match)"
                    title="Удалить"
                    :disabled="isLoading"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                  
                  <button
                    class="btn btn-outline-success btn-sm"
                    @click="onMatchEditClick(match)"
                    data-bs-toggle="modal"
                    data-bs-target="#editMatchModal"
                    title="Редактировать"
                    :disabled="isLoading"
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
  <div class="modal fade" id="editMatchModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">
            <i class="bi bi-pencil-square me-2"></i>Редактировать матч
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
          <form @submit.prevent.stop="onUpdateMatch">
            <div class="row g-3">
              <div class="col-6">
                <div class="form-floating">
                  <select class="form-select" v-model="matchToEdit.tournament" :disabled="isLoading">
                    <option :value="null">Без турнира</option>
                    <option :value="tournament.id" v-for="tournament in tournaments" :key="tournament.id">
                      {{ tournament.name }}
                    </option>
                  </select>
                  <label>Турнир</label>
                </div>
              </div>
              <div class="col-6">
                <div class="form-floating">
                  <input
                    type="datetime-local"
                    class="form-control"
                    v-model="matchToEdit.match_date"
                    :disabled="isLoading"
                  />
                  <label>Дата и время матча</label>
                </div>
              </div>
              <div class="col-4">
                <div class="form-floating">
                  <select class="form-select" v-model="matchToEdit.team1" :disabled="isLoading">
                    <option :value="null">Выберите команду</option>
                    <option :value="team.id" v-for="team in teams" :key="team.id">
                      {{ team.name }}
                    </option>
                  </select>
                  <label>Команда 1</label>
                </div>
              </div>
              <div class="col-4">
                <div class="form-floating">
                  <input
                    type="number"
                    class="form-control"
                    v-model="matchToEdit.team1_score"
                    placeholder="0"
                    min="0"
                    :disabled="isLoading"
                  />
                  <label>Счёт команды 1</label>
                </div>
              </div>
              <div class="col-4">
                <div class="form-floating">
                  <select class="form-select" v-model="matchToEdit.team2" :disabled="isLoading">
                    <option :value="null">Выберите команду</option>
                    <option :value="team.id" v-for="team in teams" :key="team.id">
                      {{ team.name }}
                    </option>
                  </select>
                  <label>Команда 2</label>
                </div>
              </div>
              <div class="col-4">
                <div class="form-floating">
                  <input
                    type="number"
                    class="form-control"
                    v-model="matchToEdit.team2_score"
                    placeholder="0"
                    min="0"
                    :disabled="isLoading"
                  />
                  <label>Счёт команды 2</label>
                </div>
              </div>
              <div class="col-12" v-if="matchToEdit.winner">
                <div class="alert alert-info">
                  <i class="bi bi-info-circle me-2"></i>
                  <strong>Текущий победитель:</strong> {{ getWinnerName(matchToEdit) }}
                  <br>
                  <small>Победитель определяется автоматически на основе счета</small>
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
            data-bs-dismiss="modal"
            type="button"
            class="btn btn-primary"
            @click="onUpdateMatch"
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
.match-card {
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.match-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #007bff;
}

.team-row {
  padding: 8px 0;
}

.team-name {
  font-weight: 500;
  font-size: 1.1rem;
}

.team-name.winner-team {
  color: #198754;
  font-weight: bold;
}

.vs-divider {
  position: relative;
}

.vs-divider::before,
.vs-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background-color: #dee2e6;
}

.vs-divider::before {
  left: 0;
}

.vs-divider::after {
  right: 0;
}

.score .badge {
  min-width: 40px;
  font-size: 1.1rem;
}

.team-logo {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.winner-section {
  border-left: 3px solid #198754;
}

.card-header {
  border-bottom: 2px solid rgba(0,0,0,0.125);
}

.btn-sm {
  padding: 0.375rem 0.75rem;
}

@media (max-width: 768px) {
  .team-name {
    font-size: 1rem;
  }
  
  .score .badge {
    font-size: 1rem;
    min-width: 35px;
  }
}
</style>