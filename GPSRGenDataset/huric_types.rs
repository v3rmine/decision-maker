pub type Atom = String;
pub type Id = u32;

#[derive(Debug)]
pub struct Huric {
    pub id: Id,
    pub prompt: String,
    pub tokens: Vec<Token>,
    pub dependencies: Vec<Dependency>,
    pub semantics_frames: Vec<SemanticFrame>,
    pub entities: Vec<Entity>,
    pub lexical_groundings: Vec<LexicalGrounding>,
}

#[derive(Debug)]
pub struct Token {
    pub id: Id,
    pub lemma: String,
    pub pos: String,
    pub surface: String,
}

#[derive(Debug)]
pub struct Dependency {
    pub from: Id,
    pub to: Id,
    pub r#type: DependencyType,
}

#[derive(Debug)]
pub enum DependencyType {}

#[derive(Debug)]
pub struct SemanticFrame {
    pub name: String,
    pub token_id: Id,
    pub elements: Vec<FrameElement>,
}

#[derive(Debug)]
pub struct FrameElement {
    pub r#type: FrameElementType,
    pub semantic_head_id: Id,
    pub tokens_id: Vec<Id>,
}

#[derive(Debug)]
pub enum FrameElementType {}

#[derive(Debug)]
pub struct Entity {
    pub atom: Atom,
    pub r#type: EntityType,
    pub attributes: Vec<Attribute>,
    pub coordinate: Option<Coordinate>,
}

#[derive(Debug)]
pub enum EntityType {}

#[derive(Debug)]
pub struct Attribute {
    pub name: String,
    pub value: String,
}

#[derive(Debug)]
pub struct Coordinate {
    pub angle: f32,
    pub x: f32,
    pub y: f32,
    pub z: f32,
}

#[derive(Debug)]
pub struct LexicalGrounding {
    pub atom: Atom,
    pub token: Id,
}
