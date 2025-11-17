/**
 * DOM Utilities - Manejo seguro de elementos DOM con type safety
 */

/**
 * Obtiene un elemento por ID con garantía de tipo
 */
export function getElement<T extends HTMLElement = HTMLElement>(
  id: string,
  selector: true
): T | null;
export function getElement<T extends HTMLElement = HTMLElement>(
  id: string,
  selector?: false
): T;
export function getElement<T extends HTMLElement = HTMLElement>(
  id: string,
  selector: boolean = false
): T | null {
  const element = document.getElementById(id) as T | null;
  if (!element && !selector) {
    throw new Error(`Element with id "${id}" not found`);
  }
  return element;
}

/**
 * Obtiene un elemento por selector con garantía de tipo
 */
export function querySelector<T extends HTMLElement = HTMLElement>(
  selector: string,
  container: Document | HTMLElement = document
): T | null {
  return container.querySelector(selector) as T | null;
}

/**
 * Obtiene todos los elementos que coincidan con un selector
 */
export function querySelectorAll<T extends HTMLElement = HTMLElement>(
  selector: string,
  container: Document | HTMLElement = document
): T[] {
  return Array.from(container.querySelectorAll(selector)) as T[];
}

/**
 * Establece el contenido de texto de un elemento
 */
export function setText(id: string, text: string): void {
  const element = getElement(id);
  element.textContent = text;
}

/**
 * Establece el contenido HTML de un elemento
 */
export function setHTML(id: string, html: string): void {
  const element = getElement(id);
  element.innerHTML = html;
}

/**
 * Establece la visibilidad de un elemento
 */
export function setVisible(id: string, visible: boolean): void {
  const element = getElement(id);
  element.style.display = visible ? '' : 'none';
}

/**
 * Obtiene el valor de un input
 */
export function getInputValue(id: string): string {
  const element = getElement<HTMLInputElement>(id);
  return element.value;
}

/**
 * Establece el valor de un input
 */
export function setInputValue(id: string, value: string): void {
  const element = getElement<HTMLInputElement>(id);
  element.value = value;
}

/**
 * Obtiene el valor de un textarea
 */
export function getTextareaValue(id: string): string {
  const element = getElement<HTMLTextAreaElement>(id);
  return element.value;
}

/**
 * Obtiene el valor seleccionado de un select
 */
export function getSelectValue(id: string): string {
  const element = getElement<HTMLSelectElement>(id);
  return element.value;
}

/**
 * Obtiene el estado de un checkbox
 */
export function getCheckboxChecked(id: string): boolean {
  const element = getElement<HTMLInputElement>(id);
  return element.checked;
}

/**
 * Establece el estado de un checkbox
 */
export function setCheckboxChecked(id: string, checked: boolean): void {
  const element = getElement<HTMLInputElement>(id);
  element.checked = checked;
}

/**
 * Agrega una clase a un elemento
 */
export function addClass(id: string, className: string): void {
  const element = getElement(id);
  element.classList.add(className);
}

/**
 * Remueve una clase de un elemento
 */
export function removeClass(id: string, className: string): void {
  const element = getElement(id);
  element.classList.remove(className);
}

/**
 * Alterna una clase en un elemento
 */
export function toggleClass(id: string, className: string): void {
  const element = getElement(id);
  element.classList.toggle(className);
}

/**
 * Verifica si un elemento tiene una clase
 */
export function hasClass(id: string, className: string): boolean {
  const element = getElement(id);
  return element.classList.contains(className);
}

/**
 * Agrega un event listener a un elemento
 */
export function addEventListener<K extends keyof HTMLElementEventMap>(
  id: string,
  event: K,
  listener: (this: HTMLElement, ev: HTMLElementEventMap[K]) => any
): void {
  const element = getElement(id);
  element.addEventListener(event, listener);
}

/**
 * Remueve un elemento del DOM
 */
export function removeElement(id: string): void {
  const element = getElement(id, true);
  if (element) {
    element.remove();
  }
}

/**
 * Limpia el contenido de un elemento
 */
export function clearElement(id: string): void {
  const element = getElement(id);
  element.innerHTML = '';
}

/**
 * Obtiene múltiples inputs como un objeto
 */
export function getFormData(
  ids: string[]
): Record<string, string> {
  const data: Record<string, string> = {};
  ids.forEach((id) => {
    data[id] = getInputValue(id);
  });
  return data;
}
