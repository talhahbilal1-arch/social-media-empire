-- =============================================================================
-- Pinterest Empire V2 — Seed Data
-- =============================================================================
-- Target project: epfoxpgrpsnhlsglxvsa (production)
-- Run this in Supabase SQL Editor AFTER supabase_migration_v2.sql
--
-- Seeds the subdomains table with initial brand subdomain configuration.
-- Uses ON CONFLICT to make this safe to re-run.
--
-- ACTION REQUIRED: Replace 'BOARD_ID_HERE' with actual Pinterest board IDs
-- after creating boards in Pinterest Business account.
-- =============================================================================


-- =============================================================================
-- Daily Deal Darling (brand = 'ddd')
-- =============================================================================
-- 5 subdomains covering the core content verticals for deal-seeking women 25-45

INSERT INTO subdomains (brand, subdomain, full_url, pinterest_board_id, pinterest_board_name, category, description, color_primary, color_secondary, posts_per_week, is_active)
VALUES
    (
        'ddd',
        'home',
        'home.dailydealdarling.com',
        'BOARD_ID_HERE',
        'Home Organization Hacks',
        'Home Organization Hacks',
        'Decluttering tips, storage solutions, small-space hacks, and home organization ideas that save money and time',
        '#E3F2FD',
        '#1976D2',
        3,
        TRUE
    ),
    (
        'ddd',
        'beauty',
        'beauty.dailydealdarling.com',
        'BOARD_ID_HERE',
        'Beauty Tips & Dupes',
        'Beauty Tips',
        'Affordable beauty routines, drugstore dupes, skincare tips, and makeup hacks for busy women',
        '#FCE4EC',
        '#C2185B',
        3,
        TRUE
    ),
    (
        'ddd',
        'kitchen',
        'kitchen.dailydealdarling.com',
        'BOARD_ID_HERE',
        'Kitchen Hacks & Recipes',
        'Kitchen Hacks',
        'Meal prep shortcuts, budget recipes, kitchen gadget reviews, and cooking tips that save time and money',
        '#FFF8E1',
        '#FFA000',
        3,
        TRUE
    ),
    (
        'ddd',
        'selfcare',
        'selfcare.dailydealdarling.com',
        'BOARD_ID_HERE',
        'Morning & Self-Care Routines',
        'Morning & Self-Care',
        'Morning routines, self-care rituals, journaling prompts, and wellness habits for busy women',
        '#E8F5E9',
        '#388E3C',
        3,
        TRUE
    ),
    (
        'ddd',
        'mom',
        'mom.dailydealdarling.com',
        'BOARD_ID_HERE',
        'Mom Life & Parenting',
        'Mom Life/Parenting',
        'Parenting hacks, kid activity ideas, mom self-care, and family organization tips on a budget',
        '#F3E5F5',
        '#7B1FA2',
        3,
        TRUE
    )
ON CONFLICT (subdomain) DO UPDATE SET
    brand = EXCLUDED.brand,
    full_url = EXCLUDED.full_url,
    pinterest_board_name = EXCLUDED.pinterest_board_name,
    category = EXCLUDED.category,
    description = EXCLUDED.description,
    color_primary = EXCLUDED.color_primary,
    color_secondary = EXCLUDED.color_secondary,
    posts_per_week = EXCLUDED.posts_per_week,
    is_active = EXCLUDED.is_active;


-- =============================================================================
-- Fit Over 35 (brand = 'fo35')
-- =============================================================================
-- 5 subdomains covering fitness content verticals for men/women 35+

INSERT INTO subdomains (brand, subdomain, full_url, pinterest_board_id, pinterest_board_name, category, description, color_primary, color_secondary, posts_per_week, is_active)
VALUES
    (
        'fo35',
        'workouts',
        'workouts.fitover35.com',
        'BOARD_ID_HERE',
        'Workout Tips & Routines',
        'Workout Tips',
        'Age-appropriate workout routines, form guides, progressive overload tips, and training splits for 35+',
        '#263238',
        '#2196F3',
        3,
        TRUE
    ),
    (
        'fo35',
        'nutrition',
        'nutrition.fitover35.com',
        'BOARD_ID_HERE',
        'Nutrition & Meal Plans',
        'Nutrition',
        'Macro-friendly recipes, meal prep guides, supplement reviews, and nutrition tips for active adults over 35',
        '#263238',
        '#4CAF50',
        3,
        TRUE
    ),
    (
        'fo35',
        'recovery',
        'recovery.fitover35.com',
        'BOARD_ID_HERE',
        'Recovery & Stretching',
        'Recovery & Stretching',
        'Stretching routines, foam rolling guides, sleep optimization, and injury prevention for aging athletes',
        '#263238',
        '#9C27B0',
        3,
        TRUE
    ),
    (
        'fo35',
        'mindset',
        'mindset.fitover35.com',
        'BOARD_ID_HERE',
        'Identity & Discipline',
        'Identity & Discipline',
        'Motivation, habit building, identity-based fitness, discipline over motivation, and mental toughness',
        '#263238',
        '#FFD700',
        3,
        TRUE
    ),
    (
        'fo35',
        'homegym',
        'homegym.fitover35.com',
        'BOARD_ID_HERE',
        'Home Gym Setup & Gear',
        'Home Gym Setup',
        'Home gym equipment reviews, garage gym builds, budget-friendly setups, and space-efficient solutions',
        '#263238',
        '#FF5722',
        3,
        TRUE
    )
ON CONFLICT (subdomain) DO UPDATE SET
    brand = EXCLUDED.brand,
    full_url = EXCLUDED.full_url,
    pinterest_board_name = EXCLUDED.pinterest_board_name,
    category = EXCLUDED.category,
    description = EXCLUDED.description,
    color_primary = EXCLUDED.color_primary,
    color_secondary = EXCLUDED.color_secondary,
    posts_per_week = EXCLUDED.posts_per_week,
    is_active = EXCLUDED.is_active;


-- =============================================================================
-- Verification query — run after seeding to confirm
-- =============================================================================
-- SELECT brand, subdomain, full_url, category, color_primary, color_secondary, is_active
-- FROM subdomains
-- ORDER BY brand, subdomain;
--
-- Expected: 10 rows (5 ddd + 5 fo35), all is_active = TRUE
