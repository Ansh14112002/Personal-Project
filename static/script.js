// script.js

// Enhanced Mobile Menu Toggle
function toggleMenu() {
  const aside = document.querySelector('aside');
  const isActive = aside.classList.toggle('active');
  
  // Add/remove backdrop when mobile menu is open
  if (isActive) {
    const backdrop = document.createElement('div');
    backdrop.className = 'fixed inset-0 bg-black/50 z-40 md:hidden transition-opacity';
    backdrop.id = 'mobile-backdrop';
    backdrop.onclick = toggleMenu;
    document.body.appendChild(backdrop);
    setTimeout(() => backdrop.style.opacity = '1', 10);
  } else {
    const backdrop = document.getElementById('mobile-backdrop');
    if (backdrop) {
      backdrop.style.opacity = '0';
      setTimeout(() => backdrop.remove(), 300);
    }
  }
}
// Enhanced Loading Function
function showLoading(form) {
  const button = form.querySelector('button');
  const loader = button.querySelector('div');
  const buttonText = button.querySelector('span');
  
  button.disabled = true;
  buttonText.textContent = 'Processing...';
  loader.classList.remove('hidden');
  loader.classList.add('loader');
  
  // Add pulse animation to card
  form.closest('.card-hover').classList.add('animate-pulse');
}

  // Set up form submissions
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', (e) => {
      if (!form.checkValidity()) return;
      showLoading(form);
      // Allow the backend to handle redirection
  });
  
  // Add ripple effect to all buttons
  document.querySelectorAll('button, a').forEach(button => {
    if (button.classList.contains('menu-toggle') || button.classList.contains('theme-toggle')) return;
    
    button.addEventListener('click', function(e) {
      if (this.disabled) return;
      
      const rect = this.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const ripple = document.createElement('span');
      ripple.className = 'ripple-effect';
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      
      this.appendChild(ripple);
      
      setTimeout(() => ripple.remove(), 1000);
    });
  });
  
  // Add hover effect to nav items
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('mouseenter', () => {
      const indicator = item.querySelector('.nav-indicator');
      indicator.style.width = '100%';
      indicator.style.opacity = '1';
    });
    
    item.addEventListener('mouseleave', () => {
      if (!item.classList.contains('active')) {
        const indicator = item.querySelector('.nav-indicator');
        indicator.style.width = '0';
        indicator.style.opacity = '0';
      }
    });
  });
  
  // Initialize active nav item indicator
  const activeNavItem = document.querySelector('.nav-item.active');
  if (activeNavItem) {
    const indicator = activeNavItem.querySelector('.nav-indicator');
    indicator.style.width = '100%';
    indicator.style.opacity = '1';
  }
});

// Animate elements when they come into view
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate__animated', 'animate__fadeInUp');
      observer.unobserve(entry.target);
    }
  });
}, {
  threshold: 0.1
});

document.querySelectorAll('.animate-on-scroll').forEach(el => {
  observer.observe(el);
});

