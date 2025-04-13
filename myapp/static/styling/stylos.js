// Select all elements with the 'carousel' class
const carousels = document.querySelectorAll(".carousel");

carousels.forEach((carousel) => {
  let isDragging = false;
  let startX, scrollLeft;

  // Apply only for non-touch devices (desktop)
  if (!("ontouchstart" in window || navigator.maxTouchPoints > 0)) {
    carousel.addEventListener("mousedown", (e) => {
      isDragging = true;
      startX = e.pageX - carousel.offsetLeft;
      scrollLeft = carousel.scrollLeft;
      carousel.style.cursor = "grabbing"; // Change cursor to indicate dragging
    });

    carousel.addEventListener("mouseleave", () => {
      isDragging = false;
      carousel.style.cursor = "grab"; // Reset cursor
    });

    carousel.addEventListener("mouseup", () => {
      isDragging = false;
      carousel.style.cursor = "grab"; // Reset cursor
    });

    carousel.addEventListener("mousemove", (e) => {
      if (!isDragging) return;

      const x = e.pageX - carousel.offsetLeft;
      const walk = (x - startX) * 2; // Adjust speed

      // Only prevent default if dragging horizontally
      if (Math.abs(walk) > 5) {
        e.preventDefault();
        carousel.scrollLeft = scrollLeft - walk;
      }
    });
  }
});

