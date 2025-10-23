<script setup>
import axios from 'axios';
import { onMounted, ref } from 'vue';

// Реактивные данные
const teams = ref([]);
const players = ref([]);
const tournaments = ref([]);
const categories = ref([]);
const matches = ref([]);
const isLoading = ref(true);
const error = ref(null);
const loadTime = ref(0);

// Данные для модального окна
const showImageModal = ref(false);
const currentImageUrl = ref('');

// Оптимизированная загрузка данных
async function loadAllData() {
  const startTime = performance.now();
  isLoading.value = true;
  error.value = null;
  
  try {
    // Параллельная загрузка всех данных
    const [teamsRes, playersRes, tournamentsRes, categoriesRes, matchesRes] = await Promise.all([
      axios.get("/api/teams/"),
      axios.get("/api/players/"),
      axios.get("/api/tournaments/"),
      axios.get("/api/tournament-categories/"),
      axios.get("/api/matches/")
    ]);
    
    // Быстрое присвоение данных
    teams.value = teamsRes.data || [];
    players.value = playersRes.data || [];
    tournaments.value = tournamentsRes.data || [];
    categories.value = categoriesRes.data || [];
    matches.value = matchesRes.data || [];
    
    const endTime = performance.now();
    loadTime.value = Math.round(endTime - startTime);
    
  } catch (err) {
    console.error('Ошибка загрузки:', err);
    error.value = err.response?.data?.message || err.message || 'Не удалось загрузить данные';
    
    // Устанавливаем пустые массивы при ошибке
    teams.value = [];
    players.value = [];
    tournaments.value = [];
    categories.value = [];
    matches.value = [];
  } finally {
    isLoading.value = false;
  }
}

// Функции для модального окна
function openImageModal(imageUrl) {
  currentImageUrl.value = imageUrl;
  showImageModal.value = true;
  
  // Блокируем прокрутку body при открытии модального окна
  document.body.style.overflow = 'hidden';
}

function closeImageModal() {
  showImageModal.value = false;
  currentImageUrl.value = '';
  
  // Восстанавливаем прокрутку body
  document.body.style.overflow = '';
}

// Закрытие модального окна по клику на фон
function onBackdropClick(event) {
  if (event.target.classList.contains('image-modal-backdrop')) {
    closeImageModal();
  }
}

// Закрытие по ESC
function onKeydown(event) {
  if (event.key === 'Escape' && showImageModal.value) {
    closeImageModal();
  }
}

// Вспомогательные функции
function getTeamName(teamId) {
  if (!teamId) return 'Не указана';
  if (typeof teamId === 'object') return teamId.name;
  return teams.value.find(t => t.id === teamId)?.name || 'Команда не найдена';
}

function getCategoryName(categoryId) {
  if (!categoryId) return 'Без категории';
  if (typeof categoryId === 'object') return categoryId.name;
  return categories.value.find(c => c.id === categoryId)?.name || 'Категория не найдена';
}

function formatDate(dateString) {
  if (!dateString) return 'Не указана';
  try {
    return new Date(dateString).toLocaleDateString('ru-RU');
  } catch {
    return 'Неверная дата';
  }
}

function isTeamWinner(match, teamId) {
  if (!match.winner) return false;
  const winnerId = typeof match.winner === 'object' ? match.winner.id : match.winner;
  const compareId = typeof teamId === 'object' ? teamId.id : teamId;
  return winnerId === compareId;
}

// Получаем команды для турнира (оптимизированно)
function getTournamentTeamsPreview(tournamentId) {
  const tournamentMatches = matches.value.filter(match => {
    const matchTournamentId = match.tournament?.id || match.tournament;
    return matchTournamentId === tournamentId;
  }).slice(0, 2);
  
  const teamNames = new Set();
  tournamentMatches.forEach(match => {
    teamNames.add(getTeamName(match.team1));
    teamNames.add(getTeamName(match.team2));
  });
  
  return Array.from(teamNames).slice(0, 3);
}

// Получаем матчи для турнира
function getTournamentMatchesCount(tournamentId) {
  return matches.value.filter(match => {
    const matchTournamentId = match.tournament?.id || match.tournament;
    return matchTournamentId === tournamentId;
  }).length;
}

// Функции для блока команд
function getTeamLogo(logoPath) {
  if (!logoPath) return '/static/images/default-team-logo.png';
  if (logoPath.startsWith('http') || logoPath.startsWith('data:')) {
    return logoPath;
  }
  return logoPath.startsWith('/') ? logoPath : `/${logoPath}`;
}

function getTeamPlayersCount(teamId) {
  return players.value.filter(player => {
    const playerTeamId = player.team?.id || player.team;
    return playerTeamId === teamId;
  }).length;
}

// Загрузка при монтировании
onMounted(() => {
  loadAllData();
  // Добавляем обработчик клавиши ESC
  document.addEventListener('keydown', onKeydown);
});
</script>

<template>
  <div class="dashboard">
    <!-- Заголовок -->
    <div class="header">
      <h1>🏆 Киберспортивная Турнирная Система</h1>
      <p>Управление турнирами, командами и матчами</p>
      <div v-if="!isLoading && !error" class="load-info">
        Данные загружены за {{ loadTime }}мс
      </div>
    </div>
    
    <!-- Индикатор загрузки -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner-container">
        <div class="spinner"></div>
        <h3>Загрузка данных...</h3>
        <p>Пожалуйста, подождите</p>
      </div>
    </div>

    <!-- Ошибка -->
    <div v-else-if="error" class="error-state">
      <div class="error-container">
        <div class="error-icon">❌</div>
        <h3>Ошибка загрузки данных</h3>
        <p>{{ error }}</p>
        <button @click="loadAllData" class="retry-btn">
          🔄 Повторить попытку
        </button>
      </div>
    </div>

    <!-- Основной контент -->
    <div v-else class="content">
      <!-- Статистика -->
      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-number">{{ teams.length }}</div>
            <div class="stat-label">Команд</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🎮</div>
            <div class="stat-number">{{ players.length }}</div>
            <div class="stat-label">Игроков</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🏆</div>
            <div class="stat-number">{{ tournaments.length }}</div>
            <div class="stat-label">Турниров</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⚔️</div>
            <div class="stat-number">{{ matches.length }}</div>
            <div class="stat-label">Матчей</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🏷️</div>
            <div class="stat-number">{{ categories.length }}</div>
            <div class="stat-label">Категорий</div>
          </div>
        </div>
      </div>

      <!-- Блок команд -->
      <div class="card mb-4">
        <div class="card-header bg-primary text-white">
          <h2>Команды</h2>
        </div>
        <div class="card-body">
          <div class="row">
            <template v-for="team in teams.slice(0, 4)" :key="team.id">
              <div class="col-md-6 mb-3">
                <div class="card team-card">
                  <div class="card-body">
                    <div class="row">
                      <div class="col-8">
                        <h5 class="card-title">{{ team.name }}</h5>
                        <p class="card-text">
                          <small class="text-muted">
                            <i class="bi bi-calendar me-1"></i>
                            Создана: {{ formatDate(team.created_at) }}
                          </small>
                        </p>
                        <p class="card-text" v-if="getTeamPlayersCount(team.id) > 0">
                          <span class="badge bg-info">
                            {{ getTeamPlayersCount(team.id) }} игроков
                          </span>
                        </p>
                        <p class="card-text" v-else>
                          <span class="badge bg-secondary">Нет игроков</span>
                        </p>
                      </div>
                      <div class="col-4" style="text-align: right;">
                        <img 
                          :src="getTeamLogo(team.logo)" 
                          @click="openImageModal(getTeamLogo(team.logo))" 
                          style="max-width:100px; border-radius:20px; max-height:100px; height:100px; cursor: pointer; object-fit: cover;"
                          :alt="team.name"
                          class="team-logo"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
            
            <!-- Состояние когда команд нет -->
            <div v-if="teams.length === 0" class="col-12 text-center py-4">
              <i class="bi bi-people display-4 text-muted d-block mb-3"></i>
              <h5 class="text-muted">Команд пока нет</h5>
              <p class="text-muted">Добавьте команды через раздел "Команды"</p>
            </div>

            <!-- Кнопка просмотра всех команд -->
            <div v-if="teams.length > 4" class="col-12 text-center mt-3">
              <router-link to="/teams" class="btn btn-outline-primary">
                <i class="bi bi-arrow-right me-2"></i>
                Показать все команды ({{ teams.length }})
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Турниры -->
      <div class="section">
        <div class="section-header">
          <h2>🎯 Активные Турниры</h2>
          <router-link to="/tournaments" class="view-all-btn">
            Все турниры →
          </router-link>
        </div>
        
        <div v-if="tournaments.length > 0" class="tournaments-grid">
          <div v-for="tournament in tournaments.slice(0, 6)" :key="tournament.id" class="tournament-card">
            <div class="tournament-header">
              <h3>{{ tournament.name }}</h3>
              <span class="matches-count">{{ getTournamentMatchesCount(tournament.id) }} матчей</span>
            </div>
            <div class="tournament-meta">
              <span class="meta-item">
                <span class="meta-icon">📅</span>
                {{ formatDate(tournament.start_date) }}
              </span>
              <span class="meta-item">
                <span class="meta-icon">🏷️</span>
                {{ getCategoryName(tournament.category) }}
              </span>
            </div>
            <div class="teams-preview">
              <span class="preview-label">Участники:</span>
              <span class="teams-list">
                {{ getTournamentTeamsPreview(tournament.id).join(', ') || 'пока нет участников' }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">📭</div>
          <h3>Турниров пока нет</h3>
          <p>Добавьте турниры через админку для отображения данных</p>
        </div>
      </div>

      <!-- Матчи -->
      <div class="section">
        <div class="section-header">
          <h2>⚡ Последние Матчи</h2>
          <router-link to="/matches" class="view-all-btn">
            Все матчи →
          </router-link>
        </div>
        
        <div v-if="matches.length > 0" class="matches-grid">
          <div v-for="match in matches.slice(0, 6)" :key="match.id" class="match-card">
            <div class="match-teams">
              <div class="team" :class="{ winner: isTeamWinner(match, match.team1) }">
                <div class="team-name">{{ getTeamName(match.team1) }}</div>
                <div class="team-score">{{ match.team1_score }}</div>
              </div>
              
              <div class="vs">VS</div>
              
              <div class="team" :class="{ winner: isTeamWinner(match, match.team2) }">
                <div class="team-name">{{ getTeamName(match.team2) }}</div>
                <div class="team-score">{{ match.team2_score }}</div>
              </div>
            </div>
            
            <div class="match-info">
              <div class="tournament-name">
                {{ getCategoryName(match.tournament?.category) }}
              </div>
              <div class="match-date">
                {{ formatDate(match.match_date) }}
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">⚽</div>
          <h3>Матчей пока нет</h3>
          <p>Добавьте матчи через админку для отображения результатов</p>
        </div>
      </div>

      <!-- Быстрые действия -->
      <div class="quick-actions">
        <h2>🚀 Быстрые действия</h2>
        <div class="actions-grid">
          <router-link to="/teams" class="action-card">
            <div class="action-icon">👥</div>
            <div class="action-text">Управление командами</div>
          </router-link>
          <router-link to="/players" class="action-card">
            <div class="action-icon">🎮</div>
            <div class="action-text">Управление игроками</div>
          </router-link>
          <router-link to="/tournaments" class="action-card">
            <div class="action-icon">🏆</div>
            <div class="action-text">Управление турнирами</div>
          </router-link>
          <router-link to="/matches" class="action-card">
            <div class="action-icon">⚔️</div>
            <div class="action-text">Управление матчами</div>
          </router-link>
          <a href="/admin" class="action-card" target="_blank">
            <div class="action-icon">⚙️</div>
            <div class="action-text">Админ-панель</div>
          </a>
        </div>
      </div>
    </div>

    <!-- Модальное окно для просмотра изображения -->
    <div 
      v-if="showImageModal" 
      class="image-modal-backdrop"
      @click="onBackdropClick"
    >
      <div class="image-modal-content">
        <button class="image-modal-close" @click="closeImageModal">
          <i class="bi bi-x-lg"></i>
        </button>
        <img 
          :src="currentImageUrl" 
          alt="Увеличенное изображение"
          class="image-modal-img"
        />
        <div class="image-modal-controls">
          <button class="btn btn-secondary" @click="closeImageModal">
            Закрыть
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Заголовок */
.header {
  background: linear-gradient(135deg, #2c3e50, #34495e);
  color: white;
  padding: 40px 30px;
  text-align: center;
}

.header h1 {
  font-size: 2.5em;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.header p {
  font-size: 1.2em;
  opacity: 0.9;
  margin-bottom: 10px;
}

.load-info {
  font-size: 0.9em;
  opacity: 0.7;
}

/* Состояния загрузки и ошибки */
.loading-state, .error-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 40px;
}

.spinner-container, .error-container {
  text-align: center;
  background: white;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

.error-icon {
  font-size: 4em;
  margin-bottom: 20px;
}

.retry-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1em;
  margin-top: 15px;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #2980b9;
  transform: translateY(-2px);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Основной контент */
.content {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Статистика */
.stats-section {
  margin-bottom: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 25px 20px;
  border-radius: 15px;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
  border-top: 4px solid #3498db;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 2.5em;
  margin-bottom: 10px;
}

.stat-number {
  font-size: 2.5em;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Блок команд */
.team-card {
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.team-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.team-logo {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 2px solid #e9ecef;
}

.team-logo:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

/* Секции */
.section {
  background: white;
  border-radius: 15px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.section-header h2 {
  color: #2c3e50;
  font-size: 1.8em;
  margin: 0;
}

.view-all-btn {
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.view-all-btn:hover {
  color: #2980b9;
}

/* Турниры */
.tournaments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.tournament-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  border-left: 4px solid #e74c3c;
  transition: transform 0.3s ease;
}

.tournament-card:hover {
  transform: translateY(-3px);
}

.tournament-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.tournament-header h3 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.3em;
}

.matches-count {
  background: #3498db;
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
}

.tournament-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7f8c8d;
  font-size: 0.9em;
}

.teams-preview {
  font-size: 0.9em;
  color: #5a6c7d;
}

.preview-label {
  font-weight: 500;
  margin-right: 5px;
}

/* Матчи */
.matches-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.match-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 20px;
  border-left: 4px solid #27ae60;
}

.match-teams {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 15px;
  align-items: center;
  margin-bottom: 15px;
}

.team {
  text-align: center;
  padding: 15px;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.team.winner {
  background: #d4edda;
  border: 2px solid #28a745;
}

.team-name {
  font-weight: bold;
  font-size: 1.1em;
  color: #2c3e50;
  margin-bottom: 8px;
}

.team-score {
  font-size: 1.8em;
  font-weight: bold;
  color: #e74c3c;
}

.vs {
  text-align: center;
  color: #7f8c8d;
  font-weight: bold;
  font-size: 1.1em;
}

.match-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #e9ecef;
}

.tournament-name {
  color: #7f8c8d;
  font-size: 0.9em;
}

.match-date {
  color: #7f8c8d;
  font-size: 0.9em;
}

/* Пустые состояния */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 4em;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin-bottom: 10px;
  color: #5a6c7d;
}

/* Быстрые действия */
.quick-actions {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.quick-actions h2 {
  color: #2c3e50;
  margin-bottom: 25px;
  font-size: 1.8em;
  text-align: center;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.action-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 25px 20px;
  text-align: center;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.action-card:hover {
  background: #3498db;
  color: white;
  transform: translateY(-5px);
  border-color: #2980b9;
}

.action-icon {
  font-size: 2.5em;
  margin-bottom: 15px;
}

.action-text {
  font-weight: 500;
  font-size: 1.1em;
}

/* Модальное окно для изображений */
.image-modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
}

.image-modal-content {
  position: relative;
  background: white;
  border-radius: 15px;
  padding: 20px;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: scaleIn 0.3s ease;
}

.image-modal-close {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  font-size: 1.2em;
  transition: background 0.3s ease;
  z-index: 1;
}

.image-modal-close:hover {
  background: rgba(0, 0, 0, 0.9);
}

.image-modal-img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  border-radius: 10px;
  margin-bottom: 15px;
}

.image-modal-controls {
  display: flex;
  gap: 10px;
  justify-content: center;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleIn {
  from { 
    opacity: 0;
    transform: scale(0.8);
  }
  to { 
    opacity: 1;
    transform: scale(1);
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .header {
    padding: 30px 20px;
  }
  
  .header h1 {
    font-size: 2em;
  }
  
  .content {
    padding: 20px;
  }
  
  .section {
    padding: 20px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .match-teams {
    grid-template-columns: 1fr;
    gap: 10px;
  }
  
  .vs {
    order: -1;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .tournaments-grid,
  .matches-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .team-card .row {
    flex-direction: column;
    text-align: center;
  }
  
  .team-card .col-4 {
    text-align: center !important;
    margin-top: 15px;
  }
  
  .image-modal-content {
    margin: 20px;
    padding: 15px;
  }
  
  .image-modal-img {
    max-height: 60vh;
  }
}
</style>