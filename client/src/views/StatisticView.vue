<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import {useUserStore} from '@/stores/user_store';
import {storeToRefs} from "pinia";

const router = useRouter()
const userStore = useUserStore()
const { userInfo } = storeToRefs(userStore)

const teamStats = ref(null)
const playerStats = ref(null)
const tournamentStats = ref(null)
const matchStats = ref(null)
const categoryStats = ref(null)
const loading = ref(false)
const error = ref(null)

// Проверяем права доступа при изменении userInfo
watch(userInfo, (newUserInfo) => {
  if (newUserInfo && newUserInfo.is_authenticated && !newUserInfo.is_staff) {
    // Если игрок (не админ) - перенаправляем на главную
    router.push('/')
  }
}, { immediate: true })

async function loadTeamStats() {
    const response = await axios.get('/api/teams/stats/')
    teamStats.value = response.data
}

async function loadPlayerStats() {
    const response = await axios.get('/api/players/stats/')
    playerStats.value = response.data
}

async function loadTournamentStats() {
    const response = await axios.get('/api/tournaments/stats/')
    tournamentStats.value = response.data
}

async function loadMatchStats() {
    const response = await axios.get('/api/matches/stats/')
    matchStats.value = response.data
}

async function loadCategoryStats() {
    const response = await axios.get('/api/tournament-categories/stats/')
    categoryStats.value = response.data
}

async function loadAllStats() {
  // Загружаем статистику только для администраторов
  if (!userInfo.value || !userInfo.value.is_staff) {
    return
  }
  
  loading.value = true
  try {
    await Promise.all([
      loadTeamStats(),
      loadPlayerStats(),
      loadTournamentStats(),
      loadMatchStats(),
      loadCategoryStats()
    ])
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Загружаем данные только если пользователь администратор
  if (userInfo.value && userInfo.value.is_staff) {
    loadAllStats()
  }
})
</script>

<template class="content">
  <div class="container pt-5">
    <!-- Показываем контент ТОЛЬКО для администраторов -->
    <div v-if="userInfo && userInfo.is_authenticated && userInfo.is_staff">
      
      <div class="text-center mb-5">
        <h1 class="display-4 text-white">📊 Статистика Турнирной Системы</h1>
      </div>

      
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
        <p class="mt-3 text-white">Загрузка статистики...</p>
      </div>

      
      <div v-if="error" class="alert alert-danger text-center">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
      </div>

      
      <div class="row g-4">
        <div class="col-12" v-if="teamStats">
          <div class="card stats-card">
            <div class="card-header bg-primary text-white">
              <h4 class="mb-0">
                <i class="bi bi-people me-2"></i>Статистика команд
              </h4>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-primary">{{ teamStats.total_teams }}</div>
                    <div class="stat-label">Всего команд</div>
                  </div>
                </div>
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-success">{{ teamStats.teams_with_players }}</div>
                    <div class="stat-label">Команд с игроками</div>
                  </div>
                </div>
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-warning">{{ teamStats.teams_without_players }}</div>
                    <div class="stat-label">Пустых команд</div>
                  </div>
                </div>
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-info">{{ teamStats.avg_players_per_team }}</div>
                    <div class="stat-label">Среднее игроков</div>
                  </div>
                </div>
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-danger">{{ teamStats.max_players_in_team }}</div>
                    <div class="stat-label">Макс. в команде</div>
                  </div>
                </div>
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-secondary">{{ teamStats.min_players_in_team }}</div>
                    <div class="stat-label">Мин. в команде</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        
        <div class="col-12" v-if="playerStats">
          <div class="card stats-card">
            <div class="card-header bg-success text-white">
              <h4 class="mb-0">
                <i class="bi bi-person me-2"></i>Статистика игроков
              </h4>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-primary">{{ playerStats.total_players }}</div>
                    <div class="stat-label">Всего игроков</div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-success">{{ playerStats.players_with_team }}</div>
                    <div class="stat-label">С командами</div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-warning">{{ playerStats.players_without_team }}</div>
                    <div class="stat-label">Без команды</div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-info">{{ playerStats.players_with_user }}</div>
                    <div class="stat-label">С аккаунтами</div>
                  </div>
                </div>
              </div>
              <div class="row mt-3">
                <div class="col-12">
                  <div class="progress" style="height: 20px;">
                    <div class="progress-bar bg-success" 
                         :style="{ width: (playerStats.players_with_team / playerStats.total_players * 100) + '%' }">
                      {{ Math.round(playerStats.players_with_team / playerStats.total_players * 100) }}% с командами
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        
        <div class="col-12" v-if="tournamentStats">
          <div class="card stats-card">
            <div class="card-header bg-warning text-dark">
              <h4 class="mb-0">
                <i class="bi bi-trophy me-2"></i>Статистика турниров
              </h4>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-primary">{{ tournamentStats.total_tournaments }}</div>
                    <div class="stat-label">Всего турниров</div>
                  </div>
                </div>
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-success">{{ tournamentStats.active_tournaments }}</div>
                    <div class="stat-label">Активных</div>
                  </div>
                </div>
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-info">{{ tournamentStats.completed_tournaments }}</div>
                    <div class="stat-label">Завершённых</div>
                  </div>
                </div>
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-warning">{{ tournamentStats.upcoming_tournaments }}</div>
                    <div class="stat-label">Предстоящих</div>
                  </div>
                </div>
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-danger">{{ tournamentStats.avg_tournament_duration }}</div>
                    <div class="stat-label">Ср. длительность (дн)</div>
                  </div>
                </div>
                <div class="col-md-2 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-secondary">{{ tournamentStats.tournaments_with_matches }}</div>
                    <div class="stat-label">С матчами</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        
        <div class="col-12" v-if="matchStats">
          <div class="card stats-card">
            <div class="card-header bg-info text-white">
              <h4 class="mb-0">
                <i class="bi bi-controller me-2"></i>Статистика матчей
              </h4>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-primary">{{ matchStats.total_matches }}</div>
                    <div class="stat-label">Всего матчей</div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-success">{{ matchStats.tournament_matches }}</div>
                    <div class="stat-label">Турнирных</div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-warning">{{ matchStats.non_tournament_matches }}</div>
                    <div class="stat-label">Внетурнирных</div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-danger">{{ matchStats.draws }}</div>
                    <div class="stat-label">Ничьих</div>
                  </div>
                </div>
              </div>
              <div class="row text-center mt-3">
                <div class="col-md-4 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-info">{{ matchStats.avg_team1_score }}</div>
                    <div class="stat-label">Ср. счёт команды 1</div>
                  </div>
                </div>
                <div class="col-md-4 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-info">{{ matchStats.avg_team2_score }}</div>
                    <div class="stat-label">Ср. счёт команды 2</div>
                  </div>
                </div>
                <div class="col-md-4 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-success">{{ matchStats.highest_scoring_match }}</div>
                    <div class="stat-label">Макс. общий счёт</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        
        <div class="col-12" v-if="categoryStats">
          <div class="card stats-card">
            <div class="card-header bg-dark text-white">
              <h4 class="mb-0">
                <i class="bi bi-tags me-2"></i>Статистика категорий
              </h4>
            </div>
            <div class="card-body">
              <div class="row text-center">
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-primary">{{ categoryStats.total_categories }}</div>
                    <div class="stat-label">Всего категорий</div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-success">{{ categoryStats.categories_with_tournaments }}</div>
                    <div class="stat-label">С турнирами</div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-warning">{{ categoryStats.categories_without_tournaments }}</div>
                    <div class="stat-label">Без турниров</div>
                  </div>
                </div>
                <div class="col-md-3 col-6 mb-3">
                  <div class="stat-item">
                    <div class="stat-number text-danger">{{ categoryStats.tournaments_in_popular_category }}</div>
                    <div class="stat-label">В популярной</div>
                  </div>
                </div>
              </div>
              <div class="row mt-3">
                <div class="col-12">
                  <div class="alert alert-primary text-center">
                    <i class="bi bi-star-fill me-2"></i>
                    <strong>Самая популярная категория:</strong> 
                    {{ categoryStats.most_popular_category }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-5">
      <div class="card bg-light">
        <div class="card-body py-5">
          <i class="bi bi-arrow-repeat display-1 text-muted d-block mb-3"></i>
          <h3 class="text-muted">Перенаправление...</h3>
          <p class="text-muted">Доступ к статистике ограничен</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

.stats-card {
  border: none;
  border-radius: 15px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
  margin-bottom: 1.5rem;
}

.stats-card:hover {
  transform: translateY(-5px);
}

.card-header {
  border-radius: 15px 15px 0 0 !important;
  padding: 1.5rem;
}

.stat-item {
  padding: 1rem;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #6c757d;
  font-weight: 500;
}

.progress {
  border-radius: 10px;
}

.progress-bar {
  border-radius: 10px;
  font-weight: 500;
}

.alert {
  border: none;
  border-radius: 10px;
  margin-bottom: 0;
}
</style>