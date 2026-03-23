//! CSV table rendering with sorting.
//!
//! Parses CSV scrape files and renders them as sortable HTML tables with HTMX-powered
//! column sorting.

use std::path::Path;

use super::helpers::render_template;
use super::loader::{self, ScrapeData, ScrapeType};
use super::routes::ViewQuery;
use super::templates::{BreadcrumbItem, CsvFragment, ErrorFragment};

/// Renders CSV data as a sortable table to an HTML string.
pub fn render_csv_html(
    full_path: &Path,
    file_path: &str,
    breadcrumbs: Vec<BreadcrumbItem>,
    query: &ViewQuery,
) -> String {
    match loader::parse_file(full_path, ScrapeType::Csv) {
        Ok(ScrapeData::Csv { headers, mut rows }) => {
            // Apply sort.
            let sort_dir = query.dir.clone().unwrap_or_else(|| "asc".to_string());
            if let Some(ref sort_col) = query.sort {
                if let Some(col_idx) = headers.iter().position(|h| h == sort_col) {
                    rows.sort_by(|a, b| {
                        let a_val = a.get(col_idx).map_or("", String::as_str);
                        let b_val = b.get(col_idx).map_or("", String::as_str);

                        // Try numeric sort first.
                        let cmp = a_val
                            .parse::<f64>()
                            .ok()
                            .zip(b_val.parse::<f64>().ok())
                            .map_or_else(
                                || a_val.cmp(b_val),
                                |(a_num, b_num)| {
                                    a_num
                                        .partial_cmp(&b_num)
                                        .unwrap_or(std::cmp::Ordering::Equal)
                                },
                            );

                        if sort_dir == "desc" {
                            cmp.reverse()
                        } else {
                            cmp
                        }
                    });
                }
            }

            let template = CsvFragment {
                breadcrumbs,
                file_path: file_path.to_string(),
                headers,
                rows,
                sort_col: query.sort.clone(),
                sort_dir,
            };
            render_template(template)
        }
        Ok(_) => render_template(ErrorFragment {
            message: "Expected CSV data".to_string(),
            status: 500,
        }),
        Err(e) => render_template(ErrorFragment {
            message: format!("Failed to parse CSV: {e}"),
            status: 500,
        }),
    }
}
