// Mobile Navigation Toggle
const hamburger = document.querySelector('.hamburger')
const navMenu = document.querySelector('.nav-menu')

hamburger.addEventListener('click', () => {
  hamburger.classList.toggle('active')
  navMenu.classList.toggle('active')
})

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-link').forEach(n =>
  n.addEventListener('click', () => {
    hamburger.classList.remove('active')
    navMenu.classList.remove('active')
  })
)

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault()
    const target = document.querySelector(this.getAttribute('href'))
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      })
    }
  })
})

// Navbar background change on scroll
window.addEventListener('scroll', () => {
  const navbar = document.querySelector('.navbar')
  if (window.scrollY > 100) {
    navbar.style.background = 'rgba(255, 255, 255, 0.98)'
    navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.15)'
  } else {
    navbar.style.background = 'rgba(255, 255, 255, 0.95)'
    navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)'
  }
})

// Lazy loading for images
const lazyImages = document.querySelectorAll('img[data-src]')

const imageObserver = new IntersectionObserver((entries, observer) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target
      img.src = img.dataset.src
      img.classList.add('loaded')
      observer.unobserve(img)
    }
  })
})

lazyImages.forEach(img => imageObserver.observe(img))

// Animate elements on scroll
const animateOnScroll = () => {
  const elements = document.querySelectorAll(
    '.feature-card, .pricing-card, .support-card'
  )

  elements.forEach(element => {
    const elementTop = element.getBoundingClientRect().top
    const elementVisible = 150

    if (elementTop < window.innerHeight - elementVisible) {
      element.style.opacity = '1'
      element.style.transform = 'translateY(0)'
    }
  })
}

// Initialize animation states
document.addEventListener('DOMContentLoaded', () => {
  const elements = document.querySelectorAll(
    '.feature-card, .pricing-card, .support-card'
  )
  elements.forEach(element => {
    element.style.opacity = '0'
    element.style.transform = 'translateY(30px)'
    element.style.transition = 'opacity 0.6s ease, transform 0.6s ease'
  })

  // Trigger initial animation check
  animateOnScroll()
})

// Add scroll event listener for animations
window.addEventListener('scroll', animateOnScroll)

// Counter animation for stats
const animateCounters = () => {
  const counters = document.querySelectorAll('.stat-number')

  counters.forEach(counter => {
    const target = parseInt(counter.textContent.replace(/[^\d]/g, ''))
    const increment = target / 100
    let current = 0

    const updateCounter = () => {
      if (current < target) {
        current += increment
        if (counter.textContent.includes('K')) {
          counter.textContent = Math.ceil(current) + 'K+'
        } else if (counter.textContent.includes('★')) {
          counter.textContent = '4.9★'
        } else {
          counter.textContent = Math.ceil(current) + '+'
        }
        setTimeout(updateCounter, 20)
      } else {
        // Keep the final value
      }
    }

    updateCounter()
  })
}

// Trigger counter animation when hero section is visible
const heroSection = document.querySelector('.hero')
const heroObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      animateCounters()
      heroObserver.unobserve(entry.target)
    }
  })
})

if (heroSection) {
  heroObserver.observe(heroSection)
}

// Pricing card hover effects
document.querySelectorAll('.pricing-card').forEach(card => {
  card.addEventListener('mouseenter', () => {
    card.style.transform = card.classList.contains('featured')
      ? 'scale(1.05) translateY(-10px)'
      : 'translateY(-10px)'
  })

  card.addEventListener('mouseleave', () => {
    card.style.transform = card.classList.contains('featured')
      ? 'scale(1.05)'
      : 'translateY(0)'
  })
})

// Feature card hover effects
document.querySelectorAll('.feature-card').forEach(card => {
  card.addEventListener('mouseenter', () => {
    card.style.transform = 'translateY(-10px)'
  })

  card.addEventListener('mouseleave', () => {
    card.style.transform = 'translateY(0)'
  })
})

// Support card hover effects
document.querySelectorAll('.support-card').forEach(card => {
  card.addEventListener('mouseenter', () => {
    card.style.transform = 'translateY(-5px)'
  })

  card.addEventListener('mouseleave', () => {
    card.style.transform = 'translateY(0)'
  })
})

// Button click animations
document.querySelectorAll('.btn').forEach(button => {
  button.addEventListener('click', function (e) {
    // Create ripple effect
    const ripple = document.createElement('span')
    const rect = this.getBoundingClientRect()
    const size = Math.max(rect.width, rect.height)
    const x = e.clientX - rect.left - size / 2
    const y = e.clientY - rect.top - size / 2

    ripple.style.width = ripple.style.height = size + 'px'
    ripple.style.left = x + 'px'
    ripple.style.top = y + 'px'
    ripple.classList.add('ripple')

    this.appendChild(ripple)

    setTimeout(() => {
      ripple.remove()
    }, 600)
  })
})

// Add ripple effect styles
const style = document.createElement('style')
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`
document.head.appendChild(style)

// Parallax effect for hero section
window.addEventListener('scroll', () => {
  const scrolled = window.pageYOffset
  const hero = document.querySelector('.hero')
  const heroImage = document.querySelector('.hero-image')

  if (hero && heroImage) {
    const rate = scrolled * -0.5
    heroImage.style.transform = `translateY(${rate}px)`
  }
})

// Typing effect for hero title
const typeWriter = (element, text, speed = 100) => {
  let i = 0
  element.innerHTML = ''

  const type = () => {
    if (i < text.length) {
      element.innerHTML += text.charAt(i)
      i++
      setTimeout(type, speed)
    }
  }

  type()
}

// Initialize typing effect when page loads
document.addEventListener('DOMContentLoaded', () => {
  const heroTitle = document.querySelector('.hero-title')
  if (heroTitle) {
    const originalText = heroTitle.textContent
    setTimeout(() => {
      typeWriter(heroTitle, originalText, 50)
    }, 500)
  }
})

// Form validation for contact forms (if any)
document.querySelectorAll('form').forEach(form => {
  form.addEventListener('submit', e => {
    e.preventDefault()

    // Basic form validation
    const inputs = form.querySelectorAll('input[required], textarea[required]')
    let isValid = true

    inputs.forEach(input => {
      if (!input.value.trim()) {
        input.style.borderColor = '#ef4444'
        isValid = false
      } else {
        input.style.borderColor = '#10b981'
      }
    })

    if (isValid) {
      // Show success message
      const successMessage = document.createElement('div')
      successMessage.textContent = 'Thank you! Your message has been sent.'
      successMessage.style.cssText = `
                background: #10b981;
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                text-align: center;
            `
      form.appendChild(successMessage)

      // Reset form
      setTimeout(() => {
        form.reset()
        successMessage.remove()
      }, 3000)
    }
  })
})

// Back to top button
const createBackToTopButton = () => {
  const button = document.createElement('button')
  button.innerHTML = '<i class="fas fa-arrow-up"></i>'
  button.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        z-index: 1000;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    `

  document.body.appendChild(button)

  // Show/hide button based on scroll position
  window.addEventListener('scroll', () => {
    if (window.pageYOffset > 300) {
      button.style.opacity = '1'
      button.style.visibility = 'visible'
    } else {
      button.style.opacity = '0'
      button.style.visibility = 'hidden'
    }
  })

  // Scroll to top when clicked
  button.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
  })

  // Hover effects
  button.addEventListener('mouseenter', () => {
    button.style.transform = 'scale(1.1)'
  })

  button.addEventListener('mouseleave', () => {
    button.style.transform = 'scale(1)'
  })
}

// Initialize back to top button
document.addEventListener('DOMContentLoaded', createBackToTopButton)

// Preloader
const createPreloader = () => {
  const preloader = document.createElement('div')
  preloader.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        transition: opacity 0.5s ease;
    `

  preloader.innerHTML = `
        <div style="text-align: center; color: white;">
            <div style="width: 50px; height: 50px; border: 3px solid rgba(255,255,255,0.3); border-top: 3px solid white; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
            <h2>WebCammerPlus</h2>
            <p>Loading...</p>
        </div>
    `

  document.body.appendChild(preloader)

  // Add spin animation
  const spinStyle = document.createElement('style')
  spinStyle.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    `
  document.head.appendChild(spinStyle)

  // Hide preloader after page loads
  window.addEventListener('load', () => {
    setTimeout(() => {
      preloader.style.opacity = '0'
      setTimeout(() => {
        preloader.remove()
      }, 500)
    }, 1000)
  })
}

// Initialize preloader
createPreloader()

// Console welcome message
console.log(
  `
%cWebCammerPlus 🎥
%cWelcome to the WebCammerPlus website!
%cBuilt with ❤️ for professional webcam recording.

%cCheck out our features:
%c• High-quality recording
%c• Intuitive video editor  
%c• Secure cloud storage
%c• Effortless sharing

%cVisit: https://github.com/jovanrlee/webcammerplus
`,
  'color: #667eea; font-size: 24px; font-weight: bold;',
  'color: #764ba2; font-size: 16px; font-weight: bold;',
  'color: #666; font-size: 14px;',
  'color: #10b981; font-size: 14px; font-weight: bold;',
  'color: #333; font-size: 12px;',
  'color: #333; font-size: 12px;',
  'color: #333; font-size: 12px;',
  'color: #333; font-size: 12px;',
  'color: #333; font-size: 12px;',
  'color: #667eea; font-size: 12px; font-weight: bold;'
)
