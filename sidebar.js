document.querySelectorAll(".icon-button").forEach(button => {
  button.addEventListener("click", () => {
    const tabId = button.dataset.tab;
    document.querySelectorAll(".tab").forEach(tab => {
      tab.style.display = "none";
    });
    document.getElementById(`tab-${tabId}`).style.display = "block";
  });
});