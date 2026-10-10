function handlePartKeydown(event, part, togglePart) {
  if (!part || (event.key !== "Enter" && event.key !== " ")) return false;
  event.preventDefault();
  togglePart(part);
  return true;
}
