use serde::{Deserialize, Serialize};

/// Categorías oficiales de productos
pub const CATEGORIAS_PRODUCTO: [&str; 4] = [
    "Nuevo conocimiento",
    "Desarrollo tecnológico",
    "Apropiación social del conocimiento",
    "Formación de recurso humano",
];

/// Estados oficiales de validación
pub const ESTADOS_VALIDACION: [&str; 3] = ["Validado", "No validado", "En revisión"];

/// Grandes categorías MinCiencias
pub const GRAN_CATEGORIAS: [(&str, &str); 4] = [
    ("GNC", "Generación de Nuevo Conocimiento"),
    ("DTI", "Desarrollo Tecnológico e Innovación"),
    ("ASC", "Apropiación Social del Conocimiento y Divulgación Pública"),
    ("FRH", "Formación de Recurso Humano para la CTeI"),
];

/// Subcategoría taxonómica según MinCiencias
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SubcategoriaTaxonomia {
    pub codigo: String,
    pub nombre: String,
    pub gran_categoria: String,
}

/// Entidad Grupo de investigación
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Grupo {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub id: Option<i64>,
    #[serde(default)]
    pub codigo_gruplac: String,
    #[serde(default)]
    pub nombre: String,
    #[serde(default)]
    pub categoria: String,
    #[serde(default)]
    pub lider: String,
    #[serde(default = "default_true")]
    pub activo: bool,
    #[serde(default)]
    pub fecha_creacion: String,
    #[serde(default)]
    pub plan: String,
}

fn default_true() -> bool {
    true
}

impl Grupo {
    pub fn new(
        id: Option<i64>,
        codigo_gruplac: impl Into<String>,
        nombre: impl Into<String>,
        categoria: impl Into<String>,
        lider: impl Into<String>,
        fecha_creacion: impl Into<String>,
        plan: impl Into<String>,
    ) -> Self {
        Self {
            id,
            codigo_gruplac: codigo_gruplac.into(),
            nombre: nombre.into(),
            categoria: categoria.into(),
            lider: lider.into(),
            activo: true,
            fecha_creacion: fecha_creacion.into(),
            plan: plan.into(),
        }
    }
}

/// Entidad Investigador
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Investigador {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub id: Option<String>,
    #[serde(default)]
    pub cedula: String,
    #[serde(default)]
    pub nombres: String,
    #[serde(default)]
    pub apellidos: String,
    #[serde(default)]
    pub email: String,
    #[serde(default = "default_true")]
    pub activo: bool,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub grupo_id: Option<i64>,
}

impl Investigador {
    pub fn new(
        id: Option<String>,
        cedula: impl Into<String>,
        nombres: impl Into<String>,
        apellidos: impl Into<String>,
        email: impl Into<String>,
        grupo_id: Option<i64>,
    ) -> Self {
        let ced_str = cedula.into();
        let final_id = id.or_else(|| Some(ced_str.clone()));
        Self {
            id: final_id,
            cedula: ced_str,
            nombres: nombres.into(),
            apellidos: apellidos.into(),
            email: email.into(),
            activo: true,
            grupo_id,
        }
    }

    pub fn nombre_completo(&self) -> String {
        let n = self.nombres.trim();
        let a = self.apellidos.trim();
        if n.is_empty() && a.is_empty() {
            format!("Investigador {}", self.cedula)
        } else if a.is_empty() {
            n.to_string()
        } else if n.is_empty() {
            a.to_string()
        } else {
            format!("{} {}", n, a)
        }
    }
}

/// Entidad Producto de investigación
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Producto {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub id: Option<String>,
    #[serde(default)]
    pub titulo: String,
    #[serde(default)]
    pub tipo: String,
    #[serde(default = "default_categoria")]
    pub categoria: String,
    #[serde(default)]
    pub validado: bool,
    #[serde(default)]
    pub anio: Option<i32>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub investigador_id: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub investigador_cedula: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub grupo_id: Option<i64>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub raw: Option<String>,
    #[serde(default = "default_gran_categoria")]
    pub gran_categoria: String,
    #[serde(default)]
    pub codigo_minciencias: String,
    #[serde(default = "default_validacion")]
    pub validacion: String,
    #[serde(default = "default_true")]
    pub activo: bool,
}

fn default_categoria() -> String {
    "Nuevo conocimiento".to_string()
}

fn default_gran_categoria() -> String {
    "Sin clasificar".to_string()
}

fn default_validacion() -> String {
    "No validado".to_string()
}

impl Producto {
    pub fn new(
        id: Option<String>,
        titulo: impl Into<String>,
        tipo: impl Into<String>,
        categoria: impl Into<String>,
        anio: Option<i32>,
        investigador_id: Option<String>,
        grupo_id: Option<i64>,
        gran_categoria: Option<String>,
        codigo_minciencias: Option<String>,
        validacion: Option<String>,
    ) -> Self {
        let cat = categoria.into();
        let cat_final = if CATEGORIAS_PRODUCTO.contains(&cat.as_str()) {
            cat
        } else {
            "Nuevo conocimiento".to_string()
        };

        let val = validacion.unwrap_or_else(|| "No validado".to_string());
        let val_final = if ESTADOS_VALIDACION.contains(&val.as_str()) {
            val
        } else {
            "No validado".to_string()
        };
        let is_valid = val_final == "Validado";

        let inv_id = investigador_id.clone();
        Self {
            id,
            titulo: titulo.into(),
            tipo: tipo.into(),
            categoria: cat_final,
            validado: is_valid,
            anio,
            investigador_id: inv_id.clone(),
            investigador_cedula: inv_id,
            grupo_id,
            raw: None,
            gran_categoria: gran_categoria.unwrap_or_else(|| "Sin clasificar".to_string()),
            codigo_minciencias: codigo_minciencias.unwrap_or_default(),
            validacion: val_final,
            activo: true,
        }
    }
}

/// Funciones auxiliares para la taxonomía MinCiencias
pub fn get_gran_categoria_nombre(sigla: &str) -> &'static str {
    match sigla.trim().to_uppercase().as_str() {
        "GNC" => "Generación de Nuevo Conocimiento",
        "DTI" => "Desarrollo Tecnológico e Innovación",
        "ASC" => "Apropiación Social del Conocimiento y Divulgación Pública",
        "FRH" => "Formación de Recurso Humano para la CTeI",
        _ => "Sin clasificar",
    }
}

pub fn normalizar_gran_categoria(gc_raw: &str) -> String {
    let s = gc_raw.trim().to_uppercase();
    if s == "GNC"
        || s.contains("NUEVO CONOCIMIENTO")
        || s.contains("GENERACION DE NUEVO CONOCIMIENTO")
        || s.contains("GENERACIÓN DE NUEVO CONOCIMIENTO")
    {
        return "GNC".to_string();
    }
    if s == "DTI"
        || s.contains("DESARROLLO TECNOLOGICO")
        || s.contains("DESARROLLO TECNOLÓGICO")
        || s.contains("INNOVACION")
        || s.contains("INNOVACIÓN")
    {
        return "DTI".to_string();
    }
    if s == "ASC"
        || s.contains("APROPIACION SOCIAL")
        || s.contains("APROPIACIÓN SOCIAL")
        || s.contains("DIVULGACION")
        || s.contains("DIVULGACIÓN")
    {
        return "ASC".to_string();
    }
    if s == "FRH"
        || s.contains("FORMACION")
        || s.contains("FORMACIÓN")
        || s.contains("RECURSO HUMANO")
        || s.contains("TALENTO HUMANO")
    {
        return "FRH".to_string();
    }
    "Sin clasificar".to_string()
}
