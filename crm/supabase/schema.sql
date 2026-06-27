-- B2B Lead Generation CRM — Supabase Schema
-- Run this in your Supabase SQL editor

-- Leads table
CREATE TABLE IF NOT EXISTS leads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT,
  phone_raw TEXT,
  email TEXT,
  website TEXT,
  address TEXT,
  niche TEXT,
  source TEXT DEFAULT 'Google Maps',  -- Google Maps | LinkedIn | Telegram | Manual
  score TEXT DEFAULT 'Cold' CHECK (score IN ('Hot', 'Warm', 'Cold')),
  status TEXT DEFAULT 'New' CHECK (status IN ('New', 'Contacted', 'Qualified', 'Won', 'Lost')),
  notes TEXT,
  rating TEXT,
  maps_url TEXT,
  query TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projects (client deliverables after Won)
CREATE TABLE IF NOT EXISTS projects (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  business_name TEXT NOT NULL,
  niche TEXT,
  website_type TEXT DEFAULT 'landing' CHECK (website_type IN ('landing', 'multipage', 'webapp', 'crm')),
  language TEXT DEFAULT 'uzbek',
  primary_color TEXT DEFAULT '#1a1a2e',
  accent_color TEXT DEFAULT '#e94560',
  phone TEXT,
  address TEXT,
  services JSONB DEFAULT '[]',
  logo_url TEXT,
  site_html_path TEXT,       -- local path to generated HTML
  netlify_url TEXT,          -- live deployed URL
  github_repo TEXT,          -- GitHub repo URL
  status TEXT DEFAULT 'Brief' CHECK (status IN ('Brief', 'Generating', 'Review', 'Deployed', 'Delivered')),
  price_uzs INTEGER,
  payment_status TEXT DEFAULT 'Unpaid' CHECK (payment_status IN ('Unpaid', 'Partial', 'Paid')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Outreach messages log
CREATE TABLE IF NOT EXISTS outreach_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  channel TEXT CHECK (channel IN ('WhatsApp', 'Telegram', 'Email', 'LinkedIn', 'Phone')),
  message TEXT,
  status TEXT DEFAULT 'Sent' CHECK (status IN ('Pending', 'Sent', 'Delivered', 'Read', 'Replied', 'Failed')),
  sent_at TIMESTAMPTZ DEFAULT NOW()
);

-- Qualifier conversations
CREATE TABLE IF NOT EXISTS qualifier_conversations (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
  chat_id BIGINT,
  platform TEXT DEFAULT 'Telegram',
  messages JSONB DEFAULT '[]',
  qualified BOOLEAN DEFAULT FALSE,
  calendly_booked BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_niche ON leads(niche);
CREATE INDEX IF NOT EXISTS idx_leads_phone ON leads(phone);
CREATE INDEX IF NOT EXISTS idx_projects_lead_id ON projects(lead_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER leads_updated_at BEFORE UPDATE ON leads
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER projects_updated_at BEFORE UPDATE ON projects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Row Level Security (enable when adding auth)
-- ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Sample data for testing
INSERT INTO leads (name, phone, niche, source, score, status, address) VALUES
('Baraka Restoran', '+998901234567', 'Restaurant', 'Google Maps', 'Hot', 'New', 'Toshkent, Yunusobod'),
('Shifo Medical', '+998912345678', 'Clinic', 'Google Maps', 'Hot', 'Contacted', 'Toshkent, Mirzo Ulug''bek'),
('BuildPro Qurilish', '+998993456789', 'Construction', 'Manual', 'Warm', 'Qualified', 'Toshkent, Chilonzor');
