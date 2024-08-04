<script setup>
import VideoPlayer from "@/components/VideoPlayer.vue";
</script>

<template>
  <div class="flex-grow flex">
    <div class="flex justify-center items-center flex-grow max-h-full">
      <VideoPlayer video-src="https://shared.cloudcrafts.club/793e4fb7-d2f5-4724-bc88-0efdf905e556.mp4"/>
    </div>
  </div>
</template>

<style>
body, #app {
  @apply min-h-screen min-w-full flex flex-col max-h-screen max-w-full;
}

</style>
