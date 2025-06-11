<template>
    <div class="translate">
        <h1>Translate</h1>
        <input type="text" v-model="text" />
        <button @click="translate">Translate</button>
    </div>
</template>

<script>
export default {
    name: 'AppTranslate'
}
</script>