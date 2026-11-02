(function () {
  document.addEventListener("DOMContentLoaded", function () {
    const userMenu = document.querySelector(".user-menu");
    const sidebar = document.getElementById("userSidebar");
    const overlay = document.getElementById("sidebarOverlay");

    if (!userMenu || !sidebar || !overlay) return;

    function openSidebar() {
      sidebar.inert = false;
      sidebar.classList.add("show");
      overlay.classList.add("show");
      userMenu.setAttribute("aria-expanded", "true");
      const first = sidebar.querySelector("a, button");
      if (first) first.focus();
    }

    function closeSidebar(returnFocus) {
      sidebar.classList.remove("show");
      overlay.classList.remove("show");
      sidebar.inert = true;
      userMenu.setAttribute("aria-expanded", "false");
      if (returnFocus) userMenu.focus();
    }

    userMenu.addEventListener("click", (e) => {
      e.stopPropagation();
      if (sidebar.classList.contains("show")) {
        closeSidebar(true);
      } else {
        openSidebar();
      }
    });

    overlay.addEventListener("click", () => closeSidebar(false));

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && sidebar.classList.contains("show")) {
        closeSidebar(true);
      }
    });

    document.addEventListener("click", (e) => {
      const isClickInside = sidebar.contains(e.target) || userMenu.contains(e.target);
      if (!isClickInside && sidebar.classList.contains("show")) {
        closeSidebar(false);
      }
    });
  });
})();
