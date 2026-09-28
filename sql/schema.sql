create table if not exists users (
  id int unsigned auto_increment primary key,
  full_name varchar(120) not null,
  email varchar(160) not null unique,
  password_hash varchar(255) not null,
  role enum('admin','operator','viewer') not null default 'operator',
  active boolean not null default true,
  created_at datetime not null default current_timestamp
);

create table if not exists categories (
  id int unsigned auto_increment primary key,
  scope varchar(50) not null,
  name varchar(100) not null,
  color_hex char(7) not null default '#16D7B0',
  active boolean not null default true,
  unique key uq_category_scope_name (scope, name)
);

create table if not exists dogs (
  id int unsigned auto_increment primary key,
  name varchar(100) not null,
  sex enum('Hembra','Macho','Desconocido') not null default 'Desconocido',
  birth_date date null,
  approx_age varchar(60) null,
  breed varchar(100) null,
  size enum('Pequeño','Mediano','Grande','Desconocido') not null default 'Desconocido',
  color varchar(100) null,
  status_category_id int unsigned null,
  admission_date date not null,
  admission_reason varchar(255) null,
  rescue_place varchar(180) null,
  sterilized boolean not null default false,
  notes text null,
  photo_url varchar(500) null,
  created_at datetime not null default current_timestamp,
  constraint fk_dog_status foreign key(status_category_id) references categories(id) on delete set null
);

create table if not exists partners (
  id int unsigned auto_increment primary key,
  name varchar(160) not null,
  partner_type_category_id int unsigned null,
  contact_name varchar(120) null,
  phone varchar(60) null,
  email varchar(160) null,
  address varchar(220) null,
  city varchar(120) null default 'Pinamar',
  cuit varchar(20) null,
  notes text null,
  active boolean not null default true,
  constraint fk_partner_type foreign key(partner_type_category_id) references categories(id) on delete set null
);

create table if not exists finance_movements (
  id int unsigned auto_increment primary key,
  movement_date date not null,
  movement_type enum('Ingreso','Gasto') not null,
  category_id int unsigned null,
  description varchar(255) not null,
  amount decimal(14,2) not null,
  payment_method varchar(80) null,
  donor_provider varchar(160) null,
  partner_id int unsigned null,
  receipt_ref varchar(160) null,
  notes text null,
  created_by int unsigned null,
  created_at datetime not null default current_timestamp,
  constraint fk_fin_category foreign key(category_id) references categories(id) on delete set null,
  constraint fk_fin_partner foreign key(partner_id) references partners(id) on delete set null,
  constraint fk_fin_user foreign key(created_by) references users(id) on delete set null
);

create table if not exists inventory_items (
  id int unsigned auto_increment primary key,
  name varchar(160) not null,
  category_id int unsigned null,
  unit varchar(50) not null default 'unidad',
  current_stock decimal(12,2) not null default 0,
  minimum_stock decimal(12,2) not null default 0,
  brand varchar(100) null,
  concentration varchar(100) null,
  expiration_date date null,
  location varchar(120) null,
  partner_id int unsigned null,
  notes text null,
  active boolean not null default true,
  constraint fk_inv_category foreign key(category_id) references categories(id) on delete set null,
  constraint fk_inv_partner foreign key(partner_id) references partners(id) on delete set null
);

create table if not exists inventory_movements (
  id int unsigned auto_increment primary key,
  item_id int unsigned not null,
  movement_date date not null,
  movement_type enum('Entrada','Salida','Ajuste') not null,
  quantity decimal(12,2) not null,
  reason varchar(180) null,
  dog_id int unsigned null,
  created_by int unsigned null,
  created_at datetime not null default current_timestamp,
  constraint fk_im_item foreign key(item_id) references inventory_items(id) on delete cascade,
  constraint fk_im_dog foreign key(dog_id) references dogs(id) on delete set null,
  constraint fk_im_user foreign key(created_by) references users(id) on delete set null
);

create table if not exists health_records (
  id int unsigned auto_increment primary key,
  dog_id int unsigned not null,
  event_date date not null,
  event_type_category_id int unsigned null,
  diagnosis text null,
  treatment text null,
  medication text null,
  veterinarian varchar(160) null,
  partner_id int unsigned null,
  weight_kg decimal(6,2) null,
  next_control_date date null,
  notes text null,
  constraint fk_hr_dog foreign key(dog_id) references dogs(id) on delete cascade,
  constraint fk_hr_type foreign key(event_type_category_id) references categories(id) on delete set null,
  constraint fk_hr_partner foreign key(partner_id) references partners(id) on delete set null
);

create table if not exists adoptions (
  id int unsigned auto_increment primary key,
  dog_id int unsigned not null,
  adoption_date date not null,
  adopter_name varchar(160) not null,
  adopter_dni varchar(30) null,
  phone varchar(60) null,
  email varchar(160) null,
  address varchar(220) null,
  city varchar(120) null,
  followup_status varchar(100) null,
  followup_date date null,
  notes text null,
  active boolean not null default true,
  constraint fk_adoption_dog foreign key(dog_id) references dogs(id) on delete cascade
);

create table if not exists castrations (
  id int unsigned auto_increment primary key,
  dog_id int unsigned null,
  external_animal_name varchar(120) null,
  species enum('Perro','Gato') not null default 'Perro',
  sex enum('Hembra','Macho','Desconocido') not null default 'Desconocido',
  castration_date date not null,
  veterinarian varchar(160) null,
  partner_id int unsigned null,
  campaign varchar(160) null,
  cost decimal(12,2) not null default 0,
  notes text null,
  constraint fk_cas_dog foreign key(dog_id) references dogs(id) on delete set null,
  constraint fk_cas_partner foreign key(partner_id) references partners(id) on delete set null
);

insert ignore into categories(scope,name,color_hex) values
('dog_status','En refugio','#16D7B0'),('dog_status','En tránsito','#3B82F6'),('dog_status','Adoptado','#7C3AED'),('dog_status','Fallecido','#14C8D4'),
('finance_income','Donación','#FFB000'),('finance_income','Evento','#16D7B0'),('finance_income','Subsidio','#3B82F6'),('finance_income','Otro ingreso','#22C55E'),
('finance_expense','Veterinaria','#F43F5E'),('finance_expense','Medicamentos','#E11D48'),('finance_expense','Alimento','#F59E0B'),('finance_expense','Traslado','#8B5CF6'),('finance_expense','Servicios','#64748B'),
('inventory','Medicamento','#14C8D4'),('inventory','Alimento','#F59E0B'),('inventory','Higiene','#3B82F6'),('inventory','Insumo veterinario','#F43F5E'),('inventory','Otro','#64748B'),
('health_event','Control','#16D7B0'),('health_event','Vacunación','#3B82F6'),('health_event','Tratamiento','#F59E0B'),('health_event','Cirugía','#F43F5E'),('health_event','Internación','#8B5CF6'),
('partner_type','Veterinaria','#F43F5E'),('partner_type','Empresa','#3B82F6'),('partner_type','Organización','#8B5CF6'),('partner_type','Proveedor','#F59E0B'),('partner_type','Municipio','#16D7B0');
