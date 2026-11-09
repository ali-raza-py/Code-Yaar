# Supabase Staging Data Comparison

**Comparison date:** 2026-11-08
**Source:** local SQLite `backend/db.sqlite3` (opened read-only)
**Target:** Supabase project `izwmyyuoklrufovmyfbi`, database `postgres`, schema `public` (PostgreSQL repeatable-read, read-only transaction)
**Scope:** detailed row-key comparison is a historical pre-sync snapshot; sync and post-sync verification results are recorded below. No row contents, credentials, or profile data are included; credential-like IDs are redacted.

## Executive summary

- Local: **74 tables**. Staging schema: **73 tables**. The authoritative sync copied all **9,257 rows across 72 model-backed tables**. `django_migrations` was preserved separately; the source-only legacy `authtoken_token` table has no current Django model/migration and was not copied.
- In the pre-transfer snapshot, **2,767** same-key rows compared equal; **3,993** same-key rows differed; **2,576** source-only keys and **3,211** staging-only keys.
- The pre-transfer snapshot identified **118** source-only rows blocked by existing unique constraints. Its structural candidate count is historical, not an authorization to copy all those rows.
- The sync verified that all 9,257 copied rows match SQLite exactly across all 72 copied tables, including the JSON field values.
- `authtoken_token` is source-only and has no staging table; it is not a candidate. Its token key is not disclosed because it is credential-like. The `django_migrations` and `django_session` tables are excluded from merge candidates (migration state and expiring sessions must not be copied as application data).

## Current integration status

- The selected source, local `db.sqlite3`, was treated as authoritative for rows in the current Django model-backed schema. The staging-only conflicting data was replaced, not retained.
- **Committed the full model-backed sync:** 9,257 rows across 72 tables. The command ran in a PostgreSQL transaction, preserved explicit primary keys, and reset sequences. The staging schema was not changed; `django_migrations` was not replaced.
- A read-only post-sync comparison verified **exact row equality** for all 9,257 rows across all 72 copied tables. It also verified 9 users, 9 groups, 82 courses, no row/column mismatches in copied tables, and the auth-user sequence is ahead of the maximum ID.
- Django `migrate --check` passed after the sync; no pending staging migrations remain. The malformed local `DATABASE_URL` entry was disabled so normal Django settings use the verified discrete Supabase `DB_*` settings. A normal-settings Django startup/system check and read-only ORM query now pass. This verifies direct Django-to-Supabase connectivity, not Cloudflare Hyperdrive.
- A consistent, reopen-verified local snapshot export of the pre-sync staging database was created (73 tables, 9,984 rows). It is stored in this session's private files directory. This is a data snapshot, not a PostgreSQL-native dump, and a restore was not tested; the transfer itself was transactional.
- Two deliberate exceptions remain: the source-only `authtoken_token` table (1 row) has no current Django model/migration or target table; and staging `django_migrations` history was preserved (75 rows) rather than overwritten with stale SQLite history (SQLite has four additional legacy `authtoken` migration records). No table was created manually.
- This was a staging-only operation. No production database/configuration, DNS, or Cloudflare deployment was changed.

## Table-by-table comparison

| Table (pre-transfer snapshot) | SQLite | Staging | Equal key+row | Same-key conflicts | SQLite-only keys | Staging-only keys | Unique-blocked | Safe candidates |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `auth_group` | 9 | 3 | 3 | 0 | 6 | 0 | 0 | 6 |
| `auth_group_permissions` | 280 | 280 | 260 | 0 | 20 | 20 | 20 | 0 |
| `auth_permission` | 276 | 276 | 276 | 0 | 0 | 0 | 0 | 0 |
| `auth_user` | 9 | 8 | 6 | 2 | 1 | 0 | 0 | 1 |
| `auth_user_groups` | 5 | 4 | 4 | 0 | 1 | 0 | 0 | 1 |
| `auth_user_user_permissions` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `authtoken_token` | 1 | N/A | 0 | 0 | 0 | 0 | 0 | 0 |
| `certificates_certificate` | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| `certificates_certificateevent` | 18 | 18 | 18 | 0 | 0 | 0 | 0 | 0 |
| `django_admin_log` | 6 | 6 | 6 | 0 | 0 | 0 | 0 | 0 |
| `django_content_type` | 69 | 69 | 69 | 0 | 0 | 0 | 0 | 0 |
| `django_migrations` | 79 | 75 | 75 | 0 | 4 | 0 | 0 | 0 |
| `django_session` | 3 | 18 | 3 | 0 | 0 | 15 | 0 | 0 |
| `learning_achievement` | 93 | 93 | 19 | 48 | 26 | 26 | 26 | 0 |
| `learning_adminactionlog` | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| `learning_announcement` | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| `learning_authenticationauditlog` | 511 | 599 | 505 | 6 | 0 | 88 | 0 | 0 |
| `learning_careertrack` | 13 | 14 | 3 | 3 | 7 | 8 | 7 | 0 |
| `learning_certification` | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| `learning_challenge` | 8 | 8 | 8 | 0 | 0 | 0 | 0 | 0 |
| `learning_challengesubmission` | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| `learning_chapter` | 422 | 440 | 15 | 254 | 153 | 171 | 6 | 0 |
| `learning_competition` | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| `learning_competitionregistration` | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| `learning_competitionresult` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_competitionsubmission` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_competitionteam` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_competitionteammember` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_course` | 82 | 83 | 3 | 47 | 32 | 33 | 32 | 0 |
| `learning_course_prerequisite_courses` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_coursecategory` | 14 | 14 | 14 | 0 | 0 | 0 | 0 | 0 |
| `learning_emailautomationrule` | 20 | 20 | 0 | 20 | 0 | 0 | 0 | 0 |
| `learning_emailcampaign` | 2 | 6 | 1 | 0 | 1 | 5 | 0 | 1 |
| `learning_emailcampaign_selected_users` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_emailcampaignrecipient` | 7 | 11 | 7 | 0 | 0 | 4 | 0 | 0 |
| `learning_emailtemplate` | 21 | 21 | 0 | 21 | 0 | 0 | 0 | 0 |
| `learning_emailtheme` | 3 | 3 | 0 | 3 | 0 | 0 | 0 | 0 |
| `learning_emailverificationtoken` | 18 | 17 | 17 | 0 | 1 | 0 | 0 | 1 |
| `learning_enrollment` | 9 | 12 | 9 | 0 | 0 | 3 | 0 | 0 |
| `learning_exercise` | 4284 | 4610 | 149 | 2494 | 1641 | 1967 | 0 | 119 |
| `learning_exerciseattempt` | 107 | 108 | 107 | 0 | 0 | 1 | 0 | 0 |
| `learning_follow` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_hint` | 205 | 205 | 205 | 0 | 0 | 0 | 0 | 0 |
| `learning_learningactivity` | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 |
| `learning_lesson` | 1450 | 1521 | 54 | 847 | 549 | 620 | 0 | 4 |
| `learning_lessonprogress` | 20 | 20 | 20 | 0 | 0 | 0 | 0 | 0 |
| `learning_maintenancesettings` | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| `learning_notificationemaillog` | 2 | 2 | 0 | 2 | 0 | 0 | 0 | 0 |
| `learning_passwordresettoken` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_platformsetting` | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| `learning_platformupdate` | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| `learning_portfolio` | 2 | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| `learning_practical` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_practicalbookmark` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_practicalclass` | 4 | 4 | 4 | 0 | 0 | 0 | 0 | 0 |
| `learning_practicalprogress` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_practicalsubject` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_progress` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_project` | 77 | 77 | 3 | 47 | 27 | 27 | 27 | 0 |
| `learning_projectimage` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_projectmilestone` | 314 | 314 | 18 | 190 | 106 | 106 | 0 | 0 |
| `learning_registrationformfield` | 15 | 15 | 15 | 0 | 0 | 0 | 0 | 0 |
| `learning_resource` | 6 | 6 | 6 | 0 | 0 | 0 | 0 | 0 |
| `learning_skill` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_snippetrun` | 2 | 3 | 2 | 0 | 0 | 1 | 0 | 0 |
| `learning_studentproject` | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| `learning_userachievement` | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 0 |
| `learning_usercertification` | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| `learning_usernotification` | 1 | 5 | 0 | 1 | 0 | 4 | 0 | 0 |
| `learning_userprofile` | 7 | 6 | 5 | 1 | 1 | 0 | 0 | 1 |
| `learning_userskill` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `learning_xptransaction` | 42 | 42 | 42 | 0 | 0 | 0 | 0 | 0 |
| `token_blacklist_blacklistedtoken` | 382 | 431 | 380 | 2 | 0 | 49 | 0 | 0 |
| `token_blacklist_outstandingtoken` | 425 | 485 | 420 | 5 | 0 | 60 | 0 | 0 |

## Exact IDs by table (pre-transfer snapshot; session-key IDs redacted)

Integer key lists use inclusive ranges (for example `4-7` means 4, 5, 6, and 7). Other key values are JSON-quoted. Composite keys are displayed as JSON arrays. `Equal` uses primary key (or `(app, name)` for `django_migrations`) and normalized common-column equality; migration applied timestamps are intentionally not compared. `Conflicts` means the same key exists on both sides but common-column values differ. Django `django_session` key IDs are intentionally redacted because they are credential-like; counts remain visible. These detailed lists and the table above are the before-transfer snapshot; the nine inserted keys are still shown as source-only in those historical lists.

### `auth_group`

- Equal IDs: 1-3
- Conflicting IDs: none
- SQLite-only IDs: 4-9
- Staging-only IDs: none
- Structurally safe merge candidate IDs (not approved for insertion): 4-9

### `auth_group_permissions`

- Equal IDs: 1-156, 3745-3748, 3909-3912, 4077-4096, 4281-4284, 4473-4484, 5285-5308, 5757-5760, 7813-7816, 8049-8052, 8289-8292, 8773-8792
- Conflicting IDs: none
- SQLite-only IDs: 10353-10364, 10909-10916
- Staging-only IDs: 9053-9060, 11473-11476, 12293-12300
- SQLite-only IDs blocked by unique constraints: 10353-10364, 10909-10916
- Unique constraint collision counts: `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (20)

### `auth_permission`

- Equal IDs: 1-276
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `auth_user`

- Equal IDs: 5, 8-9, 11-13
- Conflicting IDs: 1-2
- SQLite-only IDs: 16
- Staging-only IDs: none
- Structurally safe merge candidate IDs (not approved for insertion): 16

### `auth_user_groups`

- Equal IDs: 1, 4, 7-8
- Conflicting IDs: none
- SQLite-only IDs: 9
- Staging-only IDs: none
- Structurally safe merge candidate IDs (not approved for insertion): 9

### `certificates_certificate`

- Equal IDs: 1-2
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `certificates_certificateevent`

- Equal IDs: 1-18
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `django_admin_log`

- Equal IDs: 1-6
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `django_content_type`

- Equal IDs: 1-69
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `django_migrations`

- Equal IDs: ["admin", "0001_initial"], ["admin", "0002_logentry_remove_auto_add"], ["admin", "0003_logentry_add_action_flag_choices"], ["auth", "0001_initial"], ["auth", "0002_alter_permission_name_max_length"], ["auth", "0003_alter_user_email_max_length"], ["auth", "0004_alter_user_username_opts"], ["auth", "0005_alter_user_last_login_null"], ["auth", "0006_require_contenttypes_0002"], ["auth", "0007_alter_validators_add_error_messages"], ["auth", "0008_alter_user_username_max_length"], ["auth", "0009_alter_user_last_name_max_length"], ["auth", "0010_alter_group_name_max_length"], ["auth", "0011_update_proxy_permissions"], ["auth", "0012_alter_user_first_name_max_length"], ["certificates", "0001_initial"], ["certificates", "0002_remove_certificate_unique_active_certificate_per_learner_course_and_more"], ["contenttypes", "0001_initial"], ["contenttypes", "0002_remove_content_type_name"], ["learning", "0001_initial"], ["learning", "0002_remove_course_estimated_hours_remove_course_total_xp_and_more"], ["learning", "0003_course_certification_enabled_and_more"], ["learning", "0004_alter_course_language"], ["learning", "0005_userprofile_education_level_and_more"], ["learning", "0006_exerciseattempt_submission_id_and_more"], ["learning", "0007_remove_xptransaction_unique_xp_award_per_user_action_reference_and_more"], ["learning", "0008_userachievement_credentials"], ["learning", "0009_remove_xptransaction_unique_xp_award_per_user_action_reference_and_more"], ["learning", "0010_remove_xptransaction_unique_xp_award_per_user_action_reference_and_more"], ["learning", "0011_chapter_source_type_chapter_textbook_board_and_more"], ["learning", "0011_practicalclass_practicalsubject_practical_and_more"], ["learning", "0012_exercise_source_type_exercise_textbook_board_and_more"], ["learning", "0012_practicalclass_board_practical_description"], ["learning", "0013_careertrack_category_careertrack_cover_image_and_more"], ["learning", "0013_practicalclass_thumbnail_practicalsubject_image"], ["learning", "0014_practicalclass_is_published"], ["learning", "0014_reorganize_learning_tracks"], ["learning", "0015_challengesubmission_and_more"], ["learning", "0015_learningactivity"], ["learning", "0016_achievement_difficulty_achievement_how_to_earn_and_more"], ["learning", "0017_userprofile_longest_streak"], ["learning", "0018_merge_20261101_2249"], ["learning", "0019_merge_0015_learningactivity_0018_merge_20261101_2249"], ["learning", "0020_portfolio_studentproject_projectimage_and_more"], ["learning", "0021_competition_competitionregistration_and_more"], ["learning", "0022_notificationemaillog_usernotification_category_and_more"], ["learning", "0023_challenge_learning_objective"], ["learning", "0024_announcement"], ["learning", "0025_platformsetting"], ["learning", "0026_maintenancesettings"], ["learning", "0027_follow"], ["learning", "0028_announcement_category_announcement_cover_image_and_more"], ["learning", "0029_alter_usernotification_type"], ["learning", "0030_coursecategory_course_archived_at_course_cover_image_and_more"], ["learning", "0031_admin_platform_provisioning"], ["learning", "0032_remove_emailcampaignrecipient_unique_campaign_recipient_and_more"], ["learning", "0033_widen_notification_email_log_category"], ["learning", "0034_emailtemplate"], ["learning", "0035_seed_default_email_templates"], ["learning", "0036_emailtheme_emailtemplate_theme_emailautomationrule"], ["learning", "0037_seed_email_themes_automations"], ["learning", "0038_userprofile_first_login_at"], ["sessions", "0001_initial"], ["token_blacklist", "0001_initial"], ["token_blacklist", "0002_outstandingtoken_jti_hex"], ["token_blacklist", "0003_auto_20171017_2007"], ["token_blacklist", "0004_auto_20171017_2013"], ["token_blacklist", "0005_remove_outstandingtoken_jti"], ["token_blacklist", "0006_auto_20171017_2113"], ["token_blacklist", "0007_auto_20171017_2214"], ["token_blacklist", "0008_migrate_to_bigautofield"], ["token_blacklist", "0010_fix_migrate_to_bigautofield"], ["token_blacklist", "0011_linearizes_history"], ["token_blacklist", "0012_alter_outstandingtoken_user"], ["token_blacklist", "0013_alter_blacklistedtoken_options_and_more"]
- Conflicting IDs: none
- SQLite-only IDs: ["authtoken", "0001_initial"], ["authtoken", "0002_auto_20160226_1747"], ["authtoken", "0003_tokenproxy"], ["authtoken", "0004_alter_tokenproxy_options"]
- Staging-only IDs: none

### `django_session`

- Equal IDs: [redacted; 3 session-key IDs]
- Conflicting IDs: [redacted; 0 session-key IDs]
- SQLite-only IDs: [redacted; 0 session-key IDs]
- Staging-only IDs: [redacted; 15 session-key IDs]

### `learning_achievement`

- Equal IDs: 1-19
- Conflicting IDs: 46-93
- SQLite-only IDs: 20-45
- Staging-only IDs: 94-119
- SQLite-only IDs blocked by unique constraints: 20-45
- Unique constraint collision counts: `learning_achievement_slug_key` (26)

### `learning_adminactionlog`

- Equal IDs: none
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: 1

### `learning_announcement`

- Equal IDs: 1
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_authenticationauditlog`

- Equal IDs: 1-505
- Conflicting IDs: 506-511
- SQLite-only IDs: none
- Staging-only IDs: 512-599

### `learning_careertrack`

- Equal IDs: 7-9
- Conflicting IDs: 2, 4, 11
- SQLite-only IDs: 10, 12-17
- Staging-only IDs: 19-26
- SQLite-only IDs blocked by unique constraints: 10, 12-17
- Unique constraint collision counts: `learning_careertrack_slug_key` (7)

### `learning_certification`

- Equal IDs: 1
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_challenge`

- Equal IDs: 1-8
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_challengesubmission`

- Equal IDs: 3
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_chapter`

- Equal IDs: 30-31, 33, 41-52
- Conflicting IDs: 1-29, 32, 34-40, 53-70, 224-422
- SQLite-only IDs: 71-223
- Staging-only IDs: 423-593
- SQLite-only IDs blocked by unique constraints: 218-223
- Unique constraint collision counts: `learning_chapter_course_id_slug_13ce46cd_uniq` (6)
- Candidate rows blocked by unresolved FK dependencies: `course_id->learning_course.id` (147 rows)

### `learning_competition`

- Equal IDs: 2
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_competitionregistration`

- Equal IDs: none
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: 1

### `learning_course`

- Equal IDs: 6-8
- Conflicting IDs: 1-5, 9, 42-82
- SQLite-only IDs: 10-41
- Staging-only IDs: 83-115
- SQLite-only IDs blocked by unique constraints: 10-41
- Unique constraint collision counts: `learning_course_slug_key` (32)

### `learning_coursecategory`

- Equal IDs: 1-14
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_emailautomationrule`

- Equal IDs: none
- Conflicting IDs: 1-20
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_emailcampaign`

- Equal IDs: 1
- Conflicting IDs: none
- SQLite-only IDs: 3
- Staging-only IDs: 4-8
- Structurally safe merge candidate IDs (not approved for insertion): 3

### `learning_emailcampaignrecipient`

- Equal IDs: 1, 3-8
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: 9-12

### `learning_emailtemplate`

- Equal IDs: none
- Conflicting IDs: 1-21
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_emailtheme`

- Equal IDs: none
- Conflicting IDs: 1-3
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_emailverificationtoken`

- Equal IDs: 1-8, 11-18, 23
- Conflicting IDs: none
- SQLite-only IDs: 24
- Staging-only IDs: none
- Structurally safe merge candidate IDs (not approved for insertion): 24

### `learning_enrollment`

- Equal IDs: 1-9
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: 10-12

### `learning_exercise`

- Equal IDs: 131-133, 138-140, 146-288
- Conflicting IDs: 1-130, 134-137, 141-145, 289-614, 2256-4284
- SQLite-only IDs: 615-2255
- Staging-only IDs: 4285-6251
- Structurally safe merge candidate IDs (not approved for insertion): 2137-2255
- Candidate rows blocked by unresolved FK dependencies: `lesson_id->learning_lesson.id` (1522 rows)

### `learning_exerciseattempt`

- Equal IDs: 1-107
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: 108

### `learning_hint`

- Equal IDs: 178-236, 541-686
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_learningactivity`

- Equal IDs: none
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: 1

### `learning_lesson`

- Equal IDs: 65-118
- Conflicting IDs: 1-64, 119-189, 739-1450
- SQLite-only IDs: 190-738
- Staging-only IDs: 1451-2070
- Structurally safe merge candidate IDs (not approved for insertion): 735-738
- Candidate rows blocked by unresolved FK dependencies: `chapter_id->learning_chapter.id` (545 rows)

### `learning_lessonprogress`

- Equal IDs: 1-20
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_maintenancesettings`

- Equal IDs: 1
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_notificationemaillog`

- Equal IDs: none
- Conflicting IDs: 1-2
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_platformsetting`

- Equal IDs: 1
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_platformupdate`

- Equal IDs: 1
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_portfolio`

- Equal IDs: 1-2
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_practicalclass`

- Equal IDs: 1-4
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_project`

- Equal IDs: 1-3
- Conflicting IDs: 31-77
- SQLite-only IDs: 4-30
- Staging-only IDs: 78-104
- SQLite-only IDs blocked by unique constraints: 4-30
- Unique constraint collision counts: `learning_project_slug_key` (27)

### `learning_projectmilestone`

- Equal IDs: 1-18
- Conflicting IDs: 125-314
- SQLite-only IDs: 19-124
- Staging-only IDs: 315-420
- Candidate rows blocked by unresolved FK dependencies: `project_id->learning_project.id` (106 rows)

### `learning_registrationformfield`

- Equal IDs: 1-15
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_resource`

- Equal IDs: 1-6
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_snippetrun`

- Equal IDs: 1-2
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: 3

### `learning_studentproject`

- Equal IDs: 1
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_userachievement`

- Equal IDs: 1-3
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_usercertification`

- Equal IDs: 1
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `learning_usernotification`

- Equal IDs: none
- Conflicting IDs: 1
- SQLite-only IDs: none
- Staging-only IDs: 2-5

### `learning_userprofile`

- Equal IDs: 1, 5, 8-10
- Conflicting IDs: 2
- SQLite-only IDs: 12
- Staging-only IDs: none
- Structurally safe merge candidate IDs (not approved for insertion): 12

### `learning_xptransaction`

- Equal IDs: 1, 13-15, 22-23, 26-27, 29, 31-35, 37-38, 41-42, 44-45, 47-67, 69
- Conflicting IDs: none
- SQLite-only IDs: none
- Staging-only IDs: none

### `token_blacklist_blacklistedtoken`

- Equal IDs: 1-380
- Conflicting IDs: 381-382
- SQLite-only IDs: none
- Staging-only IDs: 383-431

### `token_blacklist_outstandingtoken`

- Equal IDs: 1-420
- Conflicting IDs: 421-425
- SQLite-only IDs: none
- Staging-only IDs: 426-485

## Schema differences


## Foreign-key dependencies

Dependency direction below is **child column -> referenced parent column**. Rows are from PostgreSQL foreign-key introspection. Candidate insertion must be parent-before-child; edges that refer to existing staging parent records do not require a parent insert.

- `auth_group_permissions.group_id` -> `auth_group.id`
- `auth_group_permissions.permission_id` -> `auth_permission.id`
- `auth_permission.content_type_id` -> `django_content_type.id`
- `auth_user_groups.group_id` -> `auth_group.id`
- `auth_user_groups.user_id` -> `auth_user.id`
- `auth_user_user_permissions.permission_id` -> `auth_permission.id`
- `auth_user_user_permissions.user_id` -> `auth_user.id`
- `certificates_certificate.course_id` -> `learning_course.id`
- `certificates_certificate.enrollment_id` -> `learning_enrollment.id`
- `certificates_certificate.issued_by_id` -> `auth_user.id`
- `certificates_certificate.supersedes_id` -> `certificates_certificate.id`
- `certificates_certificate.user_id` -> `auth_user.id`
- `certificates_certificateevent.certificate_id` -> `certificates_certificate.id`
- `certificates_certificateevent.performed_by_id` -> `auth_user.id`
- `django_admin_log.content_type_id` -> `django_content_type.id`
- `django_admin_log.user_id` -> `auth_user.id`
- `learning_adminactionlog.actor_id` -> `auth_user.id`
- `learning_announcement.created_by_id` -> `auth_user.id`
- `learning_authenticationauditlog.user_id` -> `auth_user.id`
- `learning_certification.track_id` -> `learning_careertrack.id`
- `learning_challengesubmission.challenge_id` -> `learning_challenge.id`
- `learning_challengesubmission.user_id` -> `auth_user.id`
- `learning_chapter.course_id` -> `learning_course.id`
- `learning_competition.organizer_id` -> `auth_user.id`
- `learning_competitionregistration.competition_id` -> `learning_competition.id`
- `learning_competitionregistration.team_id` -> `learning_competitionteam.id`
- `learning_competitionregistration.user_id` -> `auth_user.id`
- `learning_competitionresult.competition_id` -> `learning_competition.id`
- `learning_competitionresult.registration_id` -> `learning_competitionregistration.id`
- `learning_competitionsubmission.registration_id` -> `learning_competitionregistration.id`
- `learning_competitionteam.competition_id` -> `learning_competition.id`
- `learning_competitionteam.leader_id` -> `auth_user.id`
- `learning_competitionteammember.team_id` -> `learning_competitionteam.id`
- `learning_competitionteammember.user_id` -> `auth_user.id`
- `learning_course.category_id` -> `learning_coursecategory.id`
- `learning_course.created_by_id` -> `auth_user.id`
- `learning_course.instructor_user_id` -> `auth_user.id`
- `learning_course.track_id` -> `learning_careertrack.id`
- `learning_course_prerequisite_courses.from_course_id` -> `learning_course.id`
- `learning_course_prerequisite_courses.to_course_id` -> `learning_course.id`
- `learning_emailautomationrule.template_id` -> `learning_emailtemplate.id`
- `learning_emailcampaign.competition_id` -> `learning_competition.id`
- `learning_emailcampaign.created_by_id` -> `auth_user.id`
- `learning_emailcampaign.related_announcement_id` -> `learning_announcement.id`
- `learning_emailcampaign.related_update_id` -> `learning_platformupdate.id`
- `learning_emailcampaign_selected_users.emailcampaign_id` -> `learning_emailcampaign.id`
- `learning_emailcampaign_selected_users.user_id` -> `auth_user.id`
- `learning_emailcampaignrecipient.campaign_id` -> `learning_emailcampaign.id`
- `learning_emailcampaignrecipient.user_id` -> `auth_user.id`
- `learning_emailtemplate.created_by_id` -> `auth_user.id`
- `learning_emailverificationtoken.user_id` -> `auth_user.id`
- `learning_enrollment.course_id` -> `learning_course.id`
- `learning_enrollment.last_lesson_id` -> `learning_lesson.id`
- `learning_enrollment.user_id` -> `auth_user.id`
- `learning_exercise.lesson_id` -> `learning_lesson.id`
- `learning_exerciseattempt.exercise_id` -> `learning_exercise.id`
- `learning_exerciseattempt.user_id` -> `auth_user.id`
- `learning_follow.follower_id` -> `auth_user.id`
- `learning_follow.following_id` -> `auth_user.id`
- `learning_hint.exercise_id` -> `learning_exercise.id`
- `learning_learningactivity.course_id` -> `learning_course.id`
- `learning_learningactivity.exercise_id` -> `learning_exercise.id`
- `learning_learningactivity.lesson_id` -> `learning_lesson.id`
- `learning_learningactivity.practical_id` -> `learning_practical.id`
- `learning_learningactivity.user_id` -> `auth_user.id`
- `learning_lesson.chapter_id` -> `learning_chapter.id`
- `learning_lesson.prerequisite_id` -> `learning_lesson.id`
- `learning_lessonprogress.lesson_id` -> `learning_lesson.id`
- `learning_lessonprogress.user_id` -> `auth_user.id`
- `learning_notificationemaillog.notification_id` -> `learning_usernotification.id`
- `learning_notificationemaillog.user_id` -> `auth_user.id`
- `learning_passwordresettoken.user_id` -> `auth_user.id`
- `learning_platformupdate.created_by_id` -> `auth_user.id`
- `learning_portfolio.user_id` -> `auth_user.id`
- `learning_practical.practical_class_id` -> `learning_practicalclass.id`
- `learning_practical.subject_id` -> `learning_practicalsubject.id`
- `learning_practicalbookmark.practical_id` -> `learning_practical.id`
- `learning_practicalbookmark.user_id` -> `auth_user.id`
- `learning_practicalprogress.practical_id` -> `learning_practical.id`
- `learning_practicalprogress.user_id` -> `auth_user.id`
- `learning_practicalsubject.practical_class_id` -> `learning_practicalclass.id`
- `learning_progress.content_type_id` -> `django_content_type.id`
- `learning_progress.user_id` -> `auth_user.id`
- `learning_project.track_id` -> `learning_careertrack.id`
- `learning_projectimage.project_id` -> `learning_studentproject.id`
- `learning_projectmilestone.project_id` -> `learning_project.id`
- `learning_registrationformfield.competition_id` -> `learning_competition.id`
- `learning_resource.course_id` -> `learning_course.id`
- `learning_snippetrun.user_id` -> `auth_user.id`
- `learning_studentproject.user_id` -> `auth_user.id`
- `learning_userachievement.achievement_id` -> `learning_achievement.id`
- `learning_userachievement.user_id` -> `auth_user.id`
- `learning_usercertification.certification_id` -> `learning_certification.id`
- `learning_usercertification.user_id` -> `auth_user.id`
- `learning_usernotification.user_id` -> `auth_user.id`
- `learning_userprofile.user_id` -> `auth_user.id`
- `learning_userskill.skill_id` -> `learning_skill.id`
- `learning_userskill.user_id` -> `auth_user.id`
- `learning_xptransaction.content_type_id` -> `django_content_type.id`
- `learning_xptransaction.user_id` -> `auth_user.id`
- `token_blacklist_blacklistedtoken.token_id` -> `token_blacklist_outstandingtoken.id`
- `token_blacklist_outstandingtoken.user_id` -> `auth_user.id`

Candidate-table insertion order (parents first): `auth_user` -> `auth_user_groups` -> `learning_emailverificationtoken` -> `learning_lesson` -> `learning_exercise` -> `learning_userprofile`

## Limitations and interpretation

- The detailed ID lists and conflict counts above describe the pre-sync snapshot; they are retained as audit history, not as current staging counts.
- The source-only legacy token table is excluded because it is not represented by the current Django models or target migrations. Importing it would require restoring/adding an app schema, which was not done.
- `django_migrations` history is deployment metadata and was intentionally preserved; schema compatibility was checked with Django migration state, not by copying migration rows.
- This confirms direct Django/PostgreSQL staging connectivity and data equality. Cloudflare Hyperdrive remains unconfigured and unverified.
- No production migration, production setting/data/schema change, DNS change, or Cloudflare deployment occurred.
