(function () {
  document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("id_avatar");
    const button = document.getElementById("avatar-replace-btn");
    const preview = document.getElementById("avatar-preview-img");
    if (!input || !button || !preview) return;

    button.addEventListener("click", () => input.click());

    input.addEventListener("change", () => {
      const file = input.files && input.files[0];
      if (!file) return;
      if (!file.type.startsWith("image/")) {
        if (window.toast) window.toast("Выберите файл изображения", { type: "error" });
        input.value = "";
        return;
      }
      preview.src = URL.createObjectURL(file);
      preview.alt = "Новый аватар, будет сохранён после нажатия «Сохранить»";
      if (window.toast) window.toast("Аватар выбран. Нажмите «Сохранить», чтобы применить.");
    });
  });
})();
