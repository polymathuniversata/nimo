// src/share-modal.js
document.addEventListener("DOMContentLoaded", () => {
  const shareButton = document.getElementById("share-btn");
  const shareModal = document.getElementById("share-modal");

  if (shareButton && shareModal) {
    shareButton.addEventListener("click", () => {
      shareModal.style.display = "block";
    });
  }
});
