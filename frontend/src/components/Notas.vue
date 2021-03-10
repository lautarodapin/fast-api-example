<template>
  <div class="notas">
    notas
  </div>
</template>

<script>
export default {
  name:"Notas",
  data(){
    return {

    }
  },
  methods:{
    getNotas(){
      this.axios.get("http://127.0.0.1:8000/notas")
      .then(response => {
        console.log(response)
      })
    },
  },
  created(){
    this.getNotas();
  }
};
</script>

<style scoped>
a {
  color: #42b983;
}
</style>