const elemento = document.getElementById("hora");

function actualizarHora() {
  const ahora = new Date();
  const horas = ahora.getHours();
  const minutos = ahora.getMinutes();
  const convertir = String(horas).padStart(2, "0");
  const convertir1 = String(minutos).padStart(2,"0");
  const union = `${convertir}:${convertir1}`;
  convertir.textContent = `${id="hora"}`;



}
