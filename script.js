const modal = document.querySelector('#modal');
const toast = document.querySelector('#toast');
const dashboardView = document.querySelector('#dashboardView');
const emptyView = document.querySelector('#emptyView');
const currentView = document.querySelector('#currentView');
const emptyTitle = document.querySelector('#emptyTitle');
const appointmentList = document.querySelector('#appointmentList');
const dateInput = document.querySelector('input[name="date"]');

dateInput.value = new Date().toISOString().slice(0, 10);

function showModal() {
  modal.hidden = false;
  document.querySelector('input[name="pet"]').focus();
}
function hideModal() { modal.hidden = true; }
function showToast(message) {
  toast.firstChild.textContent = message + ' ';
  toast.classList.add('show');
  window.setTimeout(() => toast.classList.remove('show'), 2800);
}
function updateCounts(result) {
  document.querySelector('[data-filter="today"] span').textContent = result.today_count;
  document.querySelector('[data-filter="tomorrow"] span').textContent = result.tomorrow_count;
  document.querySelector('[data-filter="week"] span').textContent = result.week_count;
  document.querySelector('.stat-card.coral>strong').textContent = result.today_count;
}

document.querySelector('#openModal').addEventListener('click', showModal);
document.querySelector('#emptyAction').addEventListener('click', showModal);
document.querySelector('#closeModal').addEventListener('click', hideModal);
modal.addEventListener('click', (event) => { if (event.target === modal) hideModal(); });
document.addEventListener('keydown', (event) => { if (event.key === 'Escape') hideModal(); });

document.querySelector('#appointmentForm').addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(event.currentTarget);
  const response = await fetch('/api/citas', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(Object.fromEntries(formData)) });
  if (!response.ok) { showToast('No se pudo registrar la cita'); return; }
  const result = await response.json();
  const appointment = result.appointment;
  const item = document.createElement('div');
  item.className = 'appointment-item';
  item.dataset.day = appointment.day;
  item.innerHTML = `<div class="time-block"><strong>${appointment.time}</strong><span>${appointment.duration}</span></div><div class="pet-avatar pet-coco">${appointment.pet.charAt(0).toUpperCase()}</div><div class="appointment-info"><strong>${appointment.pet} <span class="species">${appointment.species}</span></strong><span>${appointment.reason} <i>•</i> ${appointment.vet}</span></div><div class="status-pill confirmed">${appointment.status}</div><button class="more-button" aria-label="Opciones de cita">•••</button>`;
  appointmentList.prepend(item);
  updateCounts(result);
  event.currentTarget.reset();
  dateInput.value = new Date().toISOString().slice(0, 10);
  hideModal();
  showToast('Cita registrada correctamente');
});

document.querySelectorAll('.filter-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.filter-tab').forEach((item) => item.classList.remove('active'));
    tab.classList.add('active');
    const filter = tab.dataset.filter;
    document.querySelectorAll('.appointment-item').forEach((item) => { item.hidden = filter === 'week' ? false : item.dataset.day !== filter; });
  });
});

document.querySelectorAll('.nav-item').forEach((item) => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.nav-item').forEach((nav) => nav.classList.remove('active'));
    item.classList.add('active');
    const view = item.dataset.view;
    currentView.textContent = view;
    const isDashboard = view === 'Resumen' || view === 'Agenda';
    dashboardView.hidden = !isDashboard;
    emptyView.hidden = isDashboard;
    emptyTitle.textContent = view;
    if (view === 'Agenda') document.querySelector('[data-filter="week"]').click();
  });
});

document.querySelector('#viewAgenda').addEventListener('click', () => document.querySelector('[data-view="Agenda"]').click());
document.querySelector('#addPet').addEventListener('click', () => { document.querySelector('[data-view="Mascotas"]').click(); showToast('Sección de mascotas abierta'); });
document.querySelectorAll('.task-list input').forEach((input) => input.addEventListener('change', () => showToast(input.checked ? 'Tarea completada' : 'Tarea reabierta')));
document.querySelector('.clinic-switcher .icon-button').addEventListener('click', () => showToast('Clínica Vida & Cola seleccionada'));
document.querySelector('.notification').addEventListener('click', () => showToast('No tienes notificaciones nuevas'));
document.querySelector('.round-arrow').addEventListener('click', () => document.querySelector('[data-view="Mascotas"]').click());
document.querySelector('.select-button').addEventListener('click', () => showToast('Mostrando actividad de junio de 2025'));
document.querySelector('.task-button').addEventListener('click', () => document.querySelector('.task-panel').scrollIntoView({ behavior: 'smooth', block: 'center' }));
document.querySelectorAll('.more-button').forEach((button) => button.addEventListener('click', () => showToast('Opciones de cita disponibles próximamente')));
appointmentList.addEventListener('click', (event) => { if (event.target.closest('.more-button')) showToast('Opciones de cita disponibles próximamente'); });
