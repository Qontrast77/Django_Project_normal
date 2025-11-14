import { createRouter, createWebHistory } from 'vue-router'
import BeginningView from '../views/BeginningView.vue'
import TeamsView from '../views/TeamsView.vue'
import PlayersView from '../views/PlayersView.vue'
import CategoriesView from '../views/CategoriesView.vue'
import TournamentsView from '../views/TournamentsView.vue'
import MatchesView from '../views/MatchesView.vue'
import StatisticView from '@/views/StatisticView.vue'

const routes = [
  {
    path: '/',
    name: 'beginning',
    component: BeginningView
  },
  {
    path: '/teams',
    name: 'teams',
    component: TeamsView
  },
  {
    path: '/players',
    name: 'players',
    component: PlayersView
  },
  {
    path: '/categories',
    name: 'categories',
    component: CategoriesView
  },
  {
    path: '/tournaments',
    name: 'tournaments',
    component: TournamentsView
  },
  {
    path: '/matches',
    name: 'matches',
    component: MatchesView
  },
  {
      path: '/statistic',
      component: StatisticView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router