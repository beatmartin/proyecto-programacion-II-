# Sistema de Gestión y Cobro de Estacionamiento

Aplicación de escritorio desarrollado en Python para administrar el ingreso y salida de vehículos, gestionar suscripciones mensuales, calcular cobros bajo distintas modalidades y consultar reportes de recaudación.

---

## Equipo y Distribución de Tareas

| Integrante | Usuario GitHub | Rol y Responsabilidades Principales |
| :--- | :--- | :--- |
| [Integrante 1] | `[@usuario1]` | **Dominio POO y Reglas de Cobro:** Clases de dominio con encapsulamiento (`__`), validaciones en setters, clase abstracta `ModalidadCobro`, herencia, polimorfismo y diagramas UML. |
| [Integrante 2] | `[@usuario2]` | **Persistencia y Servicios:** Modelos ORM con SQLAlchemy y SQLite, transacciones atómicas (`commit`/`rollback`), integridad de datos y generador de datos de prueba. |
| [Integrante 3] | `[@usuario3]` | **Programación Funcional e Interfaz Gráfica:** Funciones puras y operaciones con `map`, `filter`, `reduce` y `lambda` para reportes/consultas, interfaz en Tkinter y manejo de errores. |

---

## Estructura del Proyecto

```text
estacionamiento-app/
├── domain/                 # Entidades de dominio (POO) y jerarquía de modalidades de cobro
├── database/               # Conexión SQLite, modelos SQLAlchemy y repositorios
├── services/               # Casos de uso y transacciones atómicas (ingresos, salidas, suscripciones)
├── processing/             # Funciones puras, filtros y cálculo funcional de reportes
├── ui/                     # Ventanas, formularios y tablas en Tkinter
├── seed.py                 # Script de carga de datos de ejemplo y casos de verificación
├── main.py                 # Punto de entrada de la aplicación
├── requirements.txt        # Dependencias del proyecto
└── README.md               # Documentación del proyecto
