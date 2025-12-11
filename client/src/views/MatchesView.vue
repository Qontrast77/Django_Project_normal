<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref, computed } from 'vue';
import { useUserStore } from '@/stores/user_store';
import { storeToRefs } from "pinia";

const userStore = useUserStore();
const { userInfo } = storeToRefs(userStore);

const matches = ref([]);
const tournaments = ref([]);
const teams = ref([]);
const players = ref([]);
const isLoading = ref(false);
const error = ref(null);
const selectedPlayerFilter = ref('all');

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

async function fetchPlayers() {
    try {
        const response = await axios.get("/api/players/");
        players.value = response.data;
    } catch (error) {
        console.error('Ошибка при загрузке игроков:', error);
        players.value = [];
    }
}

onBeforeMount(async () => {
    await fetchMatches();
    await fetchTournaments();
    await fetchTeams();
    await fetchPlayers();
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
  if (userInfo.value.is_staff && !userInfo.value.second) {
        alert('Для редактирования требуется двухфакторная аутентификация. Нажмите кнопку "Войти по второму фактору" на главной странице.');
        return;
    }
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


function resetFilter() {
    selectedPlayerFilter.value = 'all';
}

const filteredMatches = computed(() => {
    if (selectedPlayerFilter.value === 'all') {
        return matches.value;
    }
    
    const playerId = parseInt(selectedPlayerFilter.value);
    const player = players.value.find(p => p.id === playerId);
    
    if (!player || !player.team) {
        return matches.value;
    }
    
    const playerTeamId = typeof player.team === 'object' ? player.team.id : player.team;
    
    return matches.value.filter(match => {
        const team1Id = typeof match.team1 === 'object' ? match.team1.id : match.team1;
        const team2Id = typeof match.team2 === 'object' ? match.team2.id : match.team2;
        
        return team1Id === playerTeamId || team2Id === playerTeamId;
    });
});


const canEditMatches = computed(() => {
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

    <!-- Только для админов -->
    <div v-if="canEditMatches" class="card mb-4">
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

    <!-- Только для админов -->
    <div v-if="canEditMatches" class="card mb-4">
      <div class="card-header bg-info text-white">
        <h3 class="mb-0">
          <i class="bi bi-funnel me-2"></i>Фильтр по игрокам
        </h3>
      </div>
      <div class="card-body">
        <div class="row align-items-center">
          <div class="col-md-6">
            <label class="form-label fw-bold">Выберите игрока для фильтрации матчей:</label>
            <select class="form-select" v-model="selectedPlayerFilter">
              <option value="all">👁️ Все матчи</option>
              <option 
                v-for="player in players" 
                :key="player.id" 
                :value="player.id"
              >
                🎮 {{ player.nickname || player.name }} 
                <template v-if="player.team">
                  ({{ getTeamName(player.team) }})
                </template>
              </option>
            </select>
          </div>
          <div class="col-md-6">
            <div v-if="selectedPlayerFilter !== 'all'" class="alert alert-info mt-3">
              <i class="bi bi-info-circle me-2"></i>
              <strong>Фильтр активен:</strong> 
              Показываются матчи игрока 
              <strong class="text-primary">
                {{ players.find(p => p.id === parseInt(selectedPlayerFilter))?.nickname || players.find(p => p.id === parseInt(selectedPlayerFilter))?.name }}
              </strong>
              <button class="btn btn-sm btn-outline-info ms-2" @click="resetFilter">
                <i class="bi bi-x me-1"></i>Сбросить
              </button>
            </div>
            <div v-else class="text-muted mt-3">
              <i class="bi bi-info-circle me-2"></i>
              Выберите игрока для просмотра его матчей
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Список матчей -->
    <div class="card">
      <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <h3 class="mb-0">
          {{ userInfo && userInfo.is_authenticated && !userInfo.is_staff ? 'Мои матчи' : 'Список матчей' }}
        </h3>
        <span class="badge bg-primary">{{ filteredMatches.length }} матчей</span>
      </div>
      <div class="card-body">
        <div v-if="filteredMatches.length === 0" class="text-center text-muted py-5">
          <i class="bi bi-emoji-frown display-1 d-block mb-3"></i>
          <h5>Матчей пока нет</h5>
          <p class="mb-0">{{ userInfo && userInfo.is_authenticated && !userInfo.is_staff ? 'Ваша команда еще не участвовала в матчах' : 'Добавьте первый матч используя форму выше' }}</p>
        </div>
        
        <div v-else class="row g-4">
          <div v-for="match in filteredMatches" :key="match.id" class="col-12 col-md-6 col-lg-4">
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

                
                <div class="vs-divider text-center my-2">
                  <span class="badge bg-secondary">VS</span>
                </div>

                
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
              
              <!-- Только для админов -->
              <div v-if="canEditMatches" class="card-footer bg-transparent">
                <div class="d-flex gap-2 justify-content-end">
                  <button 
                    class="btn btn-outline-danger btn-sm" 
                    @click="onRemoveClick(match)"
                    title="Удалить"
                    :disabled="isLoading"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16">
  <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z"/>
</svg>
                  </button>
                  
                  <button
                    class="btn btn-outline-success btn-sm"
                    @click="onMatchEditClick(match)"
                    data-bs-toggle="modal"
                    data-bs-target="#editMatchModal"
                    title="Редактировать"
                    :disabled="isLoading"
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

  <!-- Модалка для редактирования (Только для админов) -->
  <div v-if="canEditMatches" class="modal fade" id="editMatchModal" tabindex="-1">
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
</style>