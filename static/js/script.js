document.addEventListener('DOMContentLoaded', function () {
  const episodesContainer = document.getElementById('episodes-container');
  const toggleBtn = document.getElementById('toggleEpisodesBtn');
  let isExpanded = false;
  let episodes = [];


  const hamburgerBtn = document.querySelector('.hamburger-menu');
  const navbar = document.querySelector('.navbar');

  if (hamburgerBtn && navbar) {
    hamburgerBtn.addEventListener('click', () => {
      navbar.classList.toggle('active');
    });


    navbar.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navbar.classList.remove('active');
      });
    });
  }



  function renderEpisodes() {
    episodesContainer.innerHTML = '';
    episodes.forEach((ep, index) => {
      const isHidden = index >= 6 ? 'hidden-episode' : '';
      const card = `
      <div class="episode-card ${isHidden}" data-link="${ep.link}">
        <div class="episode-image">
          <img src="${ep.thumbnail}" alt="${ep.title}" loading="lazy" decoding="async">
          <div class="play-overlay" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s;">
            <i class="fab fa-youtube" style="font-size: 2.5rem; color: #fff;"></i>
          </div>
        </div>
        <div class="episode-content">
          <h3>${ep.title}</h3>
          <p class="episode-date">
            <i class="fab fa-youtube"></i> Video de YouTube
          </p>
          <div class="episode-actions">
            <a href="${ep.link}" class="btn btn-small btn-primary" target="_blank" rel="noopener noreferrer">
              <i class="fas fa-play"></i> Ver Video
            </a>
          </div>
        </div>
      </div>
    `;
      episodesContainer.innerHTML += card;
    });


    document.querySelectorAll('.episode-card').forEach(card => {
      const overlay = card.querySelector('.play-overlay');
      if (overlay) {
        card.addEventListener('mouseenter', () => {
          overlay.style.opacity = '1';
        });
        card.addEventListener('mouseleave', () => {
          overlay.style.opacity = '0';
        });
      }
    });
  }




  if (episodesContainer) {
    episodesContainer.addEventListener('click', (e) => {

      const interactive = e.target.closest('a, button');
      if (interactive) return;

      const card = e.target.closest('.episode-card');
      if (!card) return;

      const link = card.getAttribute('data-link');
      if (link) window.open(link, '_blank', 'noopener');
    });


    episodesContainer.addEventListener('keydown', (e) => {
      if (!['Enter', ' '].includes(e.key)) return;
      const card = e.target.closest('.episode-card');
      if (!card) return;
      const link = card.getAttribute('data-link');
      if (link) {
        e.preventDefault();
        window.open(link, '_blank', 'noopener');
      }
    });


    fetch('/api/youtube_videos')
      .then(response => response.json())
      .then(data => {
        episodes = data;
        renderEpisodes();
      })
      .catch(error => {
        console.error('Error loading YouTube videos:', error);
        episodesContainer.innerHTML = '<p style="text-align:center; color:#999;">Error al cargar los episodios recientes.</p>';
      });
  }


  if (toggleBtn && episodesContainer) {
    toggleBtn.addEventListener('click', function (e) {
      e.preventDefault();
      isExpanded = !isExpanded;
      document.querySelectorAll('.hidden-episode').forEach(card => {
        card.style.display = isExpanded ? 'flex' : 'none';
      });
      toggleBtn.textContent = isExpanded ? 'Ver menos episodios' : 'Ver todos los episodios';
    });
  }
});

function submitParticipationForm() {
  const name = document.getElementById('part-name').value;
  const email = document.getElementById('part-email').value;
  const phone = document.getElementById('part-phone').value;
  const message = document.getElementById('part-message').value;

  if (!name || !email || !message) {
    alert('Por favor, completa los campos requeridos');
    return;
  }

  fetch('/api/participation', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: name,
      email: email,
      phone: phone || null,
      message: message
    })
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        alert('¡Gracias por tu solicitud! Te contactaremos pronto.');
        document.getElementById('participationForm').reset();
      } else {
        alert('Hubo un error al enviar tu solicitud. Intenta de nuevo.');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Error al enviar la solicitud.');
    });
}

function sendEmail() {

  var email = document.getElementById('email').value;
  var subject = document.getElementById('subject').value;
  var message = document.getElementById('message').value;

  var mailtoLink = "mailto:contacto@unpodcastseguro.com" +
    "?subject=" + encodeURIComponent(subject) +
    "&body=" + encodeURIComponent(email + "\n\n" + message);

  window.open(mailtoLink, '_blank');
}

document.addEventListener('DOMContentLoaded', function () {
  loadRecommendations();
  loadNewsletters();
  loadAwards();
});

function loadRecommendations() {
  const container = document.getElementById('recommendations-container');
  if (!container) return;

  fetch('/api/recommendations')
    .then(response => response.json())
    .then(data => {
      if (Array.isArray(data) && data.length > 0) {
        container.innerHTML = data.map(rec => `
          <div class="testimonial-card">
            <p class="testimonial-text">${rec.recommendation_text}</p>
            <p class="testimonial-author">— ${rec.guest_name}${rec.episode_title ? `, ${rec.episode_title}` : ''}</p>
          </div>
        `).join('');
      }
    })
    .catch(error => console.error('Error loading recommendations:', error));
}

function loadNewsletters() {

  return;
}

function loadAwards() {
  const container = document.getElementById('awards-container');
  if (!container) return;

  fetch('/api/awards')
    .then(response => response.json())
    .then(data => {
      if (Array.isArray(data) && data.length > 0) {
        container.innerHTML = data.map(award => `
          <div class="award-badge">
            ${award.image_url ? `<img src="${award.image_url}" alt="${award.title}" class="award-image">` : ''}
            <h4>${award.title}</h4>
            ${award.description ? `<p>${award.description}</p>` : ''}
            ${award.award_date ? `<p class="award-date">${new Date(award.award_date).toLocaleDateString('es-ES')}</p>` : ''}
          </div>
        `).join('');
      }
    })
    .catch(error => console.error('Error loading awards:', error));
}


document.addEventListener('DOMContentLoaded', function () {
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);


  document.querySelectorAll('section').forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(30px)';
    section.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    observer.observe(section);
  });
});




let docTitle = document.title;
window.addEventListener("blur", () => {
  document.title = "¡Vuelve!";
});
window.addEventListener("focus", () => {
  document.title = docTitle;
});
