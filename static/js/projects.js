(function () {
  const NETWORK_ERROR = "Нет связи с сервером. Проверьте подключение и попробуйте ещё раз.";

  function notify(message, type) {
    if (window.toast) window.toast(message, { type: type || "info" });
    else alert(message);
  }

  async function postJson(url) {
    let response;
    try {
      response = await fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": window.getCookie ? window.getCookie("csrftoken") : "",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });
    } catch (err) {
      return { ok: false, message: NETWORK_ERROR };
    }
    let data = null;
    try {
      data = await response.json();
    } catch (err) {
      data = null;
    }
    if (response.ok && data && data.status === "ok") return { ok: true, data };
    if (data && data.message) return { ok: false, message: data.message };
    if (response.status === 403) {
      return { ok: false, message: "Недостаточно прав или сессия устарела. Обновите страницу." };
    }
    return { ok: false, message: `Не удалось выполнить действие (код ${response.status}).` };
  }

  document.addEventListener("DOMContentLoaded", function () {
    const completeBtn = document.getElementById("complete-project-btn");
    if (completeBtn) {
      completeBtn.addEventListener("click", async function (e) {
        e.preventDefault();
        const projectId = completeBtn.dataset.id;
        if (!projectId) return;
        if (!window.confirm("Завершить проект? Новые участники больше не смогут присоединиться.")) return;

        const result = await postJson(`/projects/${projectId}/complete/`);
        if (!result.ok) {
          notify(result.message, "error");
          return;
        }
        const statusEl = document.querySelector(".project-status-black");
        if (statusEl) {
          statusEl.textContent = "Закрыт";
          statusEl.classList.add("is-closed");
        }
        completeBtn.remove();
        notify("Проект завершён");
      });
    }

    const participateBtn = document.getElementById("participate-btn");
    const participantsList = document.getElementById("participants-list");
    const participantsCount = document.getElementById("participants-count");
    if (participateBtn && participantsList && participantsCount) {
      const userId = participateBtn.dataset.userId || null;
      const projectId = participateBtn.dataset.project;
      const userName = participateBtn.dataset.userName || "";
      const userAvatar = participateBtn.dataset.userAvatar || "";
      const isClosed = () => {
        const statusEl = document.querySelector(".project-status-black");
        return statusEl && statusEl.classList.contains("is-closed");
      };

      participateBtn.addEventListener("click", async function (e) {
        e.preventDefault();
        if (!projectId) return;
        participateBtn.disabled = true;
        const result = await postJson(`/projects/${projectId}/toggle-participate/`);
        participateBtn.disabled = false;

        if (!result.ok) {
          notify(result.message, "error");
          return;
        }

        if (result.data.participant) {
          participateBtn.textContent = "Отказаться от участия";

          const noParticipants = document.getElementById("no-participants");
          if (noParticipants) noParticipants.remove();

          const link = document.createElement("a");
          link.href = `/users/${userId}/`;
          link.id = `participant-${userId}`;
          const item = document.createElement("div");
          item.className = "participant-item";
          const img = document.createElement("img");
          img.src = userAvatar;
          img.alt = "";
          img.className = "participant-avatar";
          const info = document.createElement("div");
          info.className = "participant-info";
          const name = document.createElement("span");
          name.className = "participant-name";
          name.textContent = userName;
          const role = document.createElement("span");
          role.className = "participant-role";
          role.textContent = "Участник";
          info.append(name, role);
          item.append(img, info);
          link.appendChild(item);
          participantsList.appendChild(link);

          participantsCount.textContent = parseInt(participantsCount.textContent, 10) + 1;
          notify("Вы присоединились к проекту");
        } else {
          const el = document.getElementById(`participant-${userId}`);
          if (el) el.remove();

          const newCount = parseInt(participantsCount.textContent, 10) - 1;
          participantsCount.textContent = newCount;

          if (newCount === 0) {
            const p = document.createElement("p");
            p.id = "no-participants";
            p.textContent = "Пока нет участников";
            participantsList.appendChild(p);
          }

          if (isClosed()) {
            const note = document.createElement("p");
            note.className = "project-closed-note";
            note.textContent = "Проект завершён, набор участников закрыт";
            participateBtn.replaceWith(note);
          } else {
            participateBtn.textContent = "Участвовать";
          }
          notify("Вы вышли из проекта");
        }
      });
    }
  });
})();
