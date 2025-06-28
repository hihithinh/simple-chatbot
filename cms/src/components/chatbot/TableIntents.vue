<script setup>
import { computed, ref, onMounted } from 'vue'
import { mdiEye, mdiPencil, mdiTrashCan, mdiPlus } from '@mdi/js'
import CardBoxModal from '@/components/CardBoxModal.vue'
import TableCheckboxCell from '@/components/TableCheckboxCell.vue'
import BaseLevel from '@/components/BaseLevel.vue'
import BaseButtons from '@/components/BaseButtons.vue'
import BaseButton from '@/components/BaseButton.vue'
import IntentService from '@/services/intent.service'

const props = defineProps({
  checkable: Boolean,
})

const emit = defineEmits(['edit', 'delete', 'view', 'create'])

const items = ref([])
const isModalDangerActive = ref(false)
const selectedItem = ref(null)

const perPage = ref(10)
const currentPage = ref(0)
const checkedRows = ref([])
const isLoading = ref(true)

const itemsPaginated = computed(() =>
  items.value.slice(perPage.value * currentPage.value, perPage.value * (currentPage.value + 1)),
)

const numPages = computed(() => Math.ceil(items.value.length / perPage.value))
const currentPageHuman = computed(() => currentPage.value + 1)

const pagesList = computed(() => {
  const pagesList = []
  for (let i = 0; i < numPages.value; i++) {
    pagesList.push(i)
  }
  return pagesList
})

const remove = (arr, cb) => {
  const newArr = []
  arr.forEach((item) => {
    if (!cb(item)) {
      newArr.push(item)
    }
  })
  return newArr
}

const checked = (isChecked, item) => {
  if (isChecked) {
    checkedRows.value.push(item)
  } else {
    checkedRows.value = remove(checkedRows.value, (row) => row.id === item.id)
  }
}

const fetchItems = async () => {
  isLoading.value = true
  try {
    const response = await IntentService.getIntents()
    items.value = response.data
  } catch (error) {
    console.error('Error fetching intents:', error)
  } finally {
    isLoading.value = false
  }
}

const confirmDelete = (item) => {
  selectedItem.value = item
  isModalDangerActive.value = true
}

const deleteItem = async () => {
  if (selectedItem.value) {
    try {
      await IntentService.deleteIntent(selectedItem.value.id)
      await fetchItems()
      emit('delete', selectedItem.value)
    } catch (error) {
      console.error('Error deleting intent:', error)
    } finally {
      isModalDangerActive.value = false
      selectedItem.value = null
    }
  }
}

onMounted(() => {
  fetchItems()
})
</script>

<template>
  <CardBoxModal v-model="isModalDangerActive" title="Xác nhận xóa" button="danger" has-cancel @confirm="deleteItem">
    <p>Bạn có chắc chắn muốn xóa intent này không?</p>
    <p v-if="selectedItem">Tên intent: <b>{{ selectedItem.name }}</b></p>
  </CardBoxModal>

  <div class="mb-4">
    <BaseButton
      color="info"
      :icon="mdiPlus"
      label="Thêm Intent mới"
      @click="emit('create')"
    />
  </div>

  <table>
    <thead>
      <tr>
        <th v-if="props.checkable" />
        <th>ID</th>
        <th>Tên Intent</th>
        <th>Mô tả</th>
        <th>Trạng thái</th>
        <th>Thao tác</th>
      </tr>
    </thead>
    <tbody v-if="!isLoading">
      <tr v-for="item in itemsPaginated" :key="item.id">
        <TableCheckboxCell v-if="props.checkable" @checked="checked($event, item)" />
        <td data-label="ID">{{ item.id }}</td>
        <td data-label="Tên Intent">{{ item.name }}</td>
        <td data-label="Mô tả">{{ item.description || 'Không có mô tả' }}</td>
        <td data-label="Trạng thái">
          <span 
            :class="[
              'rounded-full px-3 py-1 text-sm', 
              item.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            ]"
          >
            {{ item.is_active ? 'Hoạt động' : 'Không hoạt động' }}
          </span>
        </td>
        <td class="before:hidden lg:w-1 whitespace-nowrap">
          <BaseButtons type="justify-start lg:justify-end" no-wrap>
            <BaseButton 
              color="info" 
              :icon="mdiEye" 
              small 
              @click="emit('view', item)" 
            />
            <BaseButton 
              color="warning" 
              :icon="mdiPencil" 
              small 
              @click="emit('edit', item)" 
            />
            <BaseButton
              color="danger"
              :icon="mdiTrashCan"
              small
              @click="confirmDelete(item)"
            />
          </BaseButtons>
        </td>
      </tr>
      <tr v-if="itemsPaginated.length === 0">
        <td colspan="6" class="text-center py-4">Không có dữ liệu</td>
      </tr>
    </tbody>
    <tbody v-else>
      <tr>
        <td colspan="6" class="text-center py-4">Đang tải dữ liệu...</td>
      </tr>
    </tbody>
  </table>
  <div v-if="numPages > 1" class="p-3 lg:px-6 border-t border-gray-100 dark:border-slate-800">
    <BaseLevel>
      <BaseButtons>
        <BaseButton
          v-for="page in pagesList"
          :key="page"
          :active="page === currentPage"
          :label="page + 1"
          :color="page === currentPage ? 'lightDark' : 'whiteDark'"
          small
          @click="currentPage = page"
        />
      </BaseButtons>
      <small>Trang {{ currentPageHuman }} / {{ numPages }}</small>
    </BaseLevel>
  </div>
</template>
