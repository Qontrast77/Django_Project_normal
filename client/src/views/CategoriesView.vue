<script setup>
import axios from 'axios';
import Cookies from 'js-cookie';
import { onBeforeMount, ref } from 'vue';

const categories = ref([]);
const isLoading = ref(false);
const error = ref(null);

onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
})

async function fetchCategories() {
    try {
        isLoading.value = true;
        error.value = null;
        const response = await axios.get("/api/tournament-categories/");
        categories.value = response.data;
    } catch (err) {
        console.error('Ошибка загрузки категорий:', err);
        error.value = err.response?.data || 'Не удалось загрузить категории';
        categories.value = [];
    } finally {
        isLoading.value = false;
    }
}

onBeforeMount(async () => {
    await fetchCategories();
})

const categoryToAdd = ref({
    name: '',
    description: ''
});

async function onCategoryAdd() {
  try {
    isLoading.value = true;
    error.value = null;
    
    if (!categoryToAdd.value.name.trim()) {
      error.value = 'Название категории обязательно для заполнения';
      return;
    }

    const data = {
      name: categoryToAdd.value.name.trim(),
      description: categoryToAdd.value.description?.trim() || ''
    };

    await axios.post("/api/tournament-categories/", data);
    await fetchCategories();
    
    categoryToAdd.value = {
        name: '',
        description: ''
    };
  } catch (err) {
    console.error('Ошибка добавления категории:', err);
    error.value = err.response?.data || 'Не удалось добавить категорию';
  } finally {
    isLoading.value = false;
  }
}

async function onRemoveClick(category) {
  if (!confirm(`Удалить категорию "${category.name}"?`)) return;
  
  try {
    await axios.delete(`/api/tournament-categories/${category.id}/`);
    await fetchCategories();
  } catch (err) {
    console.error('Ошибка удаления категории:', err);
    error.value = err.response?.data || 'Не удалось удалить категорию';
  }
}

const categoryToEdit = ref({
    name: '',
    description: ''
});

function onCategoryEditClick(category) {
  categoryToEdit.value = { 
    ...category,
    name: category.name || '',
    description: category.description || ''
  };
}

async function onUpdateCategory() {
  try {
    isLoading.value = true;
    error.value = null;
    
    if (!categoryToEdit.value.name.trim()) {
      error.value = 'Название категории обязательно для заполнения';
      return;
    }

    const data = {
      name: categoryToEdit.value.name.trim(),
      description: categoryToEdit.value.description?.trim() || ''
    };

    await axios.put(`/api/tournament-categories/${categoryToEdit.value.id}/`, data);
    await fetchCategories();
    
  } catch (err) {
    console.error('Ошибка обновления категории:', err);
    error.value = err.response?.data || 'Не удалось обновить категорию';
  } finally {
    isLoading.value = false;
  }
}

function truncateDescription(description, maxLength = 50) {
  if (!description) return 'Описание отсутствует';
  if (description.length <= maxLength) return description;
  return description.substring(0, maxLength) + '...';
}
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

    <!-- Форма добавления категории -->
    <div class="card mb-4">
      <div class="card-header bg-primary text-white">
        <h3 class="mb-0">Добавить категорию турнира</h3>
      </div>
      <div class="card-body">
        <form @submit.prevent.stop="onCategoryAdd">
          <div class="row g-3">
            <div class="col-md-5">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="categoryToAdd.name"
                  placeholder="Название категории"
                  required
                  :disabled="isLoading"
                />
                <label>Название категории</label>
              </div>
            </div>
            <div class="col-md-5">
              <div class="form-floating">
                <input
                  type="text"
                  class="form-control"
                  v-model="categoryToAdd.description"
                  placeholder="Описание категории"
                  :disabled="isLoading"
                />
                <label>Описание категории</label>
              </div>
            </div>
            <div class="col-md-2">
              <button type="submit" class="btn btn-primary h-100 w-100" :disabled="isLoading">
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                Добавить
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>

    <!-- Список категорий -->
    <div class="card">
      <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <h3 class="mb-0">Список категорий турниров</h3>
        <span class="badge bg-primary">{{ categories.length }} категорий</span>
      </div>
      <div class="card-body">
        <div v-if="categories.length === 0" class="text-center text-muted py-5">
          <i class="bi bi-tags display-1 d-block mb-3"></i>
          <h5>Категорий пока нет</h5>
          <p class="mb-0">Добавьте первую категорию используя форму выше</p>
        </div>
        
        <div v-else class="row g-4">
          <div v-for="category in categories" :key="category.id" class="col-12 col-md-6 col-lg-4 col-xl-3">
            <div class="category-card card h-100">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <h5 class="card-title mb-0">{{ category.name }}</h5>
                  <span class="badge bg-info">ID: {{ category.id }}</span>
                </div>
                
                <p class="card-text text-muted">
                  {{ truncateDescription(category.description) }}
                </p>
              </div>
              
              <div class="card-footer bg-transparent">
                <div class="d-flex gap-2 justify-content-end">
                  <button 
                    class="btn btn-outline-danger btn-sm" 
                    @click="onRemoveClick(category)"
                    :disabled="isLoading"
                    title="Удалить"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                  
                  <button
                    class="btn btn-outline-success btn-sm"
                    @click="onCategoryEditClick(category)"
                    data-bs-toggle="modal"
                    data-bs-target="#editCategoryModal"
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
  <div class="modal fade" id="editCategoryModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5">
            <i class="bi bi-pencil-square me-2"></i>Редактировать категорию
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
          <form @submit.prevent.stop="onUpdateCategory">
            <div class="row g-3">
              <div class="col-12">
                <div class="form-floating">
                  <input
                    type="text"
                    class="form-control"
                    v-model="categoryToEdit.name"
                    placeholder="Название категории"
                    required
                    :disabled="isLoading"
                  />
                  <label>Название категории</label>
                </div>
              </div>
              <div class="col-12">
                <div class="form-floating">
                  <textarea
                    class="form-control"
                    v-model="categoryToEdit.description"
                    placeholder="Описание категории"
                    :disabled="isLoading"
                    style="height: 100px;"
                  ></textarea>
                  <label>Описание категории</label>
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
            @click="onUpdateCategory"
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
.category-card {
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  border-color: #007bff;
}

.card-title {
  color: #2c3e50;
  font-weight: 600;
}

.card-text {
  font-size: 0.9rem;
  line-height: 1.4;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
}

.card-header {
  border-bottom: 2px solid rgba(0,0,0,0.125);
}

/* Адаптивность */
@media (max-width: 768px) {
  .category-card {
    margin-bottom: 1rem;
  }
}
</style>