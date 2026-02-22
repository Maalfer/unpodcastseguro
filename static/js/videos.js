document.addEventListener("DOMContentLoaded", () => {
  const contenedor = document.getElementById("episodios-lista");
  const buscador = document.getElementById("buscador-episodios");
  const btnVerMas = document.getElementById("btn-ver-mas");
  const totalEpisodesEl = document.getElementById("total-episodes");

  let episodios = [];
  let visibles = 6; // Aumentamos el número inicial
  let isLoading = false;

  // Cargar episodios
  loadEpisodes();
  // Cargar videos de YouTube
  loadYoutubeVideos();

  async function loadEpisodes() {
    try {
      showLoadingState();
      const response = await fetch("/api/episodios");
      const data = await response.json();
      episodios = data;

      if (totalEpisodesEl) {
        totalEpisodesEl.textContent = episodios.length;
      }

      renderEpisodios();
      hideLoadingState();
    } catch (error) {
      console.error('Error loading episodes:', error);
      showError('Error al cargar los episodios');
    }
  }

  function showLoadingState() {
    contenedor.innerHTML = `
      <div class="loading-state">
        <div class="loading-spinner">
          <i class="fas fa-spinner fa-spin"></i>
        </div>
        <p>Cargando episodios...</p>
      </div>
    `;
  }

  function hideLoadingState() {
    const loadingState = document.querySelector('.loading-state');
    if (loadingState) {
      loadingState.remove();
    }
  }

  function showError(message) {
    contenedor.innerHTML = `
      <div class="error-state">
        <i class="fas fa-exclamation-triangle"></i>
        <p>${message}</p>
        <button class="btn btn-secondary" onclick="location.reload()">
          <i class="fas fa-redo"></i>
          Reintentar
        </button>
      </div>
    `;
  }

  function renderEpisodios(filtro = "") {
    contenedor.innerHTML = "";

    let episodiosFiltrados = episodios.filter(ep =>
      ep.titulo.toLowerCase().includes(filtro.toLowerCase()) ||
      ep.descripcion.toLowerCase().includes(filtro.toLowerCase()) ||
      ep.fecha.toLowerCase().includes(filtro.toLowerCase())
    );

    // Mostrar todos los resultados si se está buscando
    const mostrar = filtro ? episodiosFiltrados : episodiosFiltrados.slice(0, visibles);

    if (mostrar.length === 0) {
      contenedor.innerHTML = `
        <div class="no-results">
          <i class="fas fa-search"></i>
          <h3>No se encontraron episodios</h3>
          <p>Intenta con otros términos de búsqueda</p>
        </div>
      `;
      btnVerMas.style.display = "none";
      return;
    }

    mostrar.forEach((ep, index) => {
      const realIndex = episodios.indexOf(ep);
      const episodeCard = createEpisodeCard(ep, realIndex, index);
      contenedor.appendChild(episodeCard);
    });

    // Mostrar u ocultar el botón "Ver más"
    if (filtro || visibles >= episodiosFiltrados.length) {
      btnVerMas.style.display = "none";
    } else {
      btnVerMas.style.display = "inline-flex";
    }

    attachFormListeners();
    animateCards();
  }

  function createEpisodeCard(ep, realIndex, displayIndex) {
    const card = document.createElement('div');
    card.className = 'episodio-form';
    card.style.animationDelay = `${displayIndex * 0.1}s`;

    card.innerHTML = `
      <div class="episode-card-header">
        <h4>
          <i class="fas fa-podcast"></i>
          Episodio #${realIndex + 1}
        </h4>
        <div class="episode-status">
          <span class="status-badge published">
            <i class="fas fa-check-circle"></i>
            Publicado
          </span>
        </div>
      </div>

      <form data-index="${realIndex}">
        <div class="form-row">
          <div class="input-group">
            <label for="titulo-${realIndex}">
              <i class="fas fa-heading"></i>
              Título del Episodio
            </label>
            <input type="text" id="titulo-${realIndex}" name="titulo" value="${ep.titulo}" required>
          </div>
        </div>

        <div class="form-row two-columns">
          <div class="input-group">
            <label for="fecha-${realIndex}">
              <i class="fas fa-calendar"></i>
              Fecha de Publicación
            </label>
            <input type="text" id="fecha-${realIndex}" name="fecha" value="${ep.fecha}" required>
          </div>
          <div class="input-group">
            <label for="duracion-${realIndex}">
              <i class="fas fa-clock"></i>
              Duración
            </label>
            <input type="text" id="duracion-${realIndex}" name="duracion" value="${ep.duracion}" required>
          </div>
        </div>

        <div class="form-row">
          <div class="input-group">
            <label for="descripcion-${realIndex}">
              <i class="fas fa-align-left"></i>
              Descripción
            </label>
            <textarea id="descripcion-${realIndex}" name="descripcion" rows="4" required>${ep.descripcion}</textarea>
          </div>
        </div>

        <div class="form-row two-columns">
          <div class="input-group">
            <label for="imagen-${realIndex}">
              <i class="fas fa-image"></i>
              Imagen (ruta en static/images)
            </label>
            <input type="text" id="imagen-${realIndex}" name="imagen" value="${ep.imagen}" required>
          </div>
          <div class="input-group">
            <label for="enlace-${realIndex}">
              <i class="fas fa-link"></i>
              Enlace del Audio
            </label>
            <input type="url" id="enlace-${realIndex}" name="enlace" value="${ep.enlace || ''}" required>
          </div>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary">
            <i class="fas fa-save"></i>
            Guardar Cambios
          </button>
          <button type="button" class="btn btn-outline preview-btn" data-index="${realIndex}">
            <i class="fas fa-eye"></i>
            Vista Previa
          </button>
          <button type="button" class="btn btn-danger delete-btn" data-index="${realIndex}">
            <i class="fas fa-trash"></i>
            Eliminar
          </button>
        </div>
      </form>
    `;

    return card;
  }

  function animateCards() {
    const cards = document.querySelectorAll('.episodio-form');
    cards.forEach((card, index) => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';

      setTimeout(() => {
        card.style.transition = 'all 0.5s ease';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
      }, index * 100);
    });
  }

  function attachFormListeners() {
    // Form submission listeners
    document.querySelectorAll(".episodio-form form").forEach(form => {
      form.addEventListener("submit", async function (e) {
        e.preventDefault();

        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;

        // Show loading state
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
        submitBtn.disabled = true;

        try {
          const data = Object.fromEntries(new FormData(this));
          const index = this.getAttribute("data-index");

          const response = await fetch(`/admin/editar_episodio/${index}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
          });

          const result = await response.json();

          if (response.ok) {
            showNotification('Episodio actualizado correctamente', 'success');
            // Update local data
            episodios[index] = { ...episodios[index], ...data };
          } else {
            showNotification(result.error || 'Error al actualizar el episodio', 'error');
          }
        } catch (error) {
          console.error('Error:', error);
          showNotification('Error de conexión', 'error');
        } finally {
          // Reset button state
          submitBtn.innerHTML = originalText;
          submitBtn.disabled = false;
        }
      });
    });

    // Preview button listeners
    document.querySelectorAll('.preview-btn').forEach(btn => {
      btn.addEventListener('click', function () {
        const index = this.dataset.index;
        const episode = episodios[index];
        showPreviewModal(episode);
      });
    });

    // Delete button listeners

    document.querySelectorAll('.delete-btn').forEach(btn => {
      btn.addEventListener('click', function () {
        const index = this.dataset.index;
        if (confirm('¿Estás seguro de que deseas eliminar este episodio? Esta acción no se puede deshacer.')) {
          fetch(`/admin/eliminar_episodio/${index}`, {
            method: 'POST',
          })
            .then(response => response.json())
            .then(data => {
              if (data.success) {
                showNotification('Episodio eliminado correctamente', 'success');
                episodios.splice(index, 1);
                renderEpisodios(buscador.value.trim());
              } else {
                showNotification(data.error || 'Error al eliminar episodio', 'error');
              }
            })
            .catch(err => {
              console.error('Error eliminando episodio:', err);
              showNotification('Error al conectar con el servidor', 'error');
            });
        }
      });
    });

  }

  function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    const icon = type === 'success' ? 'check-circle' :
      type === 'error' ? 'exclamation-triangle' : 'info-circle';

    notification.innerHTML = `
      <i class="fas fa-${icon}"></i>
      <span>${message}</span>
      <button class="close-notification">
        <i class="fas fa-times"></i>
      </button>
    `;

    document.body.appendChild(notification);

    // Show notification
    setTimeout(() => notification.classList.add('show'), 100);

    // Auto-hide after 5 seconds
    setTimeout(() => hideNotification(notification), 5000);

    // Close button listener
    notification.querySelector('.close-notification').addEventListener('click', () => {
      hideNotification(notification);
    });
  }

  function hideNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
  }

  function showPreviewModal(episode) {
    // Implementation for preview modal
    console.log('Preview episode:', episode);
  }

  function showDeleteConfirmation(index) {
    if (confirm('¿Estás seguro de que deseas eliminar este episodio? Esta acción no se puede deshacer.')) {
      // Implementation for delete functionality
      console.log('Delete episode at index:', index);
    }
  }

  // Search functionality with debounce
  let searchTimeout;
  buscador.addEventListener("input", (e) => {
    clearTimeout(searchTimeout);
    const query = e.target.value.trim();

    searchTimeout = setTimeout(() => {
      visibles = 6; // Reset visible count when searching
      renderEpisodios(query);
    }, 300);
  });

  // Load more functionality
  btnVerMas.addEventListener("click", () => {
    if (isLoading) return;

    isLoading = true;
    btnVerMas.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cargando...';

    setTimeout(() => {
      visibles += 6;
      renderEpisodios(buscador.value.trim());

      btnVerMas.innerHTML = '<i class="fas fa-chevron-down"></i> Cargar más episodios';
      isLoading = false;

      if (visibles >= episodios.length) {
        btnVerMas.style.display = "none";
      }
    }, 500); // Simulate loading time
  });

  // Filter buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      this.classList.add('active');

      const filter = this.dataset.filter;
      // Implement filtering logic based on filter type
      console.log('Filter by:', filter);
    });
  });
  function loadYoutubeVideos() {
    const container = document.getElementById('youtube-videos-lista');
    if (!container) return;

    fetch('/api/youtube_videos')
      .then(response => response.json())
      .then(videos => {
        container.innerHTML = '';

        if (videos.length === 0) {
          container.innerHTML = `
                <div class="no-results">
                    <i class="fab fa-youtube"></i>
                    <p>No se encontraron videos o falta configurar el ID del canal.</p>
                </div>
            `;
          return;
        }

        videos.forEach(video => {
          const date = new Date(video.published).toLocaleDateString();
          const card = document.createElement('div');
          card.className = 'video-card';
          card.innerHTML = `
                <a href="${video.link}" target="_blank" class="video-thumbnail-wrapper">
                    <img src="${video.thumbnail}" alt="${video.title}" class="video-thumbnail">
                    <div class="play-overlay"><i class="fas fa-play"></i></div>
                </a>
                <div class="video-info">
                    <a href="${video.link}" target="_blank" class="video-title">${video.title}</a>
                    <span class="video-date"><i class="far fa-clock"></i> ${date}</span>
                </div>
            `;
          container.appendChild(card);
        });
      })
      .catch(err => {
        console.error('Error loading YouTube videos:', err);
        container.innerHTML = '<p class="error-text">Error al cargar los videos.</p>';
      });
  }
});





