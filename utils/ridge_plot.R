# Required packages
library(ggplot2)
library(ggridges)
library(dplyr)
library(tidyr)
library(jsonlite)

# Read data
data <- fromJSON("sentence_token_histogram.json")

# Data processing function
process_dataset <- function(dataset_name, data_type = "all") {  # Added data_type parameter
  dataset <- data[[dataset_name]][[data_type]]  # Use data_type to select subset
  result_list <- list()
  
  for (lang in intersect(c('english', 'farsi', 'kurmanji', 'translation'), names(dataset))) {
    if (length(dataset[[lang]]) > 0 && !all(dataset[[lang]] == 0)) {
      df <- data.frame(
        tokens = rep(as.numeric(names(dataset[[lang]])), 
                     times = as.numeric(unlist(dataset[[lang]]))),
        dataset = factor(dataset_name, 
                         levels = sort(c("BQI", "GLK", "HAC", "LKI", "MZN", "SDH", "TLY", "ZZA"))),
        type = lang
      )
      result_list[[length(result_list) + 1]] <- df
    }
  }
  
  if (length(result_list) > 0) return(bind_rows(result_list))
  return(NULL)
}

# Create plotting function
create_token_plot <- function(data_type = "all") {
  # Process datasets
  plot_data <- bind_rows(lapply(c("BQI", "GLK", "HAC", "LKI", "MZN", "SDH", "TLY", "ZZA"), 
                                function(x) process_dataset(x, data_type)))
  
  # Custom transformation for x-axis
  custom_trans <- scales::trans_new(
    "custom",
    transform = function(x) ifelse(x <= 20, x, 20 + (x - 20) / 15),
    inverse = function(x) ifelse(x <= 20, x, 20 + (x - 20) * 15)
  )
  
  # Create plot
  ggplot(plot_data, aes(x = tokens, y = dataset, fill = type)) + 
    geom_density_ridges(
      stat = "density",
      aes(height = after_stat(density)),
      scale = 10,           
      alpha = 0.5,         
      rel_min_height = 0,
      adjust = 1.5         
    ) +
    scale_x_continuous(
      trans = custom_trans,
      breaks = c(seq(0, 20, by = 5), 40, 60),  
      limits = NULL  
    ) +
    coord_cartesian(clip = "off") +
    labs(
      x = "Number of Tokens",
      y = "Languages",
      fill = ""
    ) +
    theme_minimal(base_size = 14) +
    scale_fill_manual(
      values = c(
        "english" = "violet",     
        "farsi" = "yellow",      
        "kurmanji" = "red",    
        "translation" = "black"
      ),
      labels = c(
        "english" = "English",
        "farsi" = "Persian",
        "kurmanji" = "Northern Kurdish",
        "translation" = "Translation"
      )
    ) +
    theme(
      legend.position = "top",
      text = element_text(family = "serif", size = 14),
      panel.grid.major.y = element_line(size = 1)
    ) +
    facet_grid(rows = vars(factor(dataset, levels = sort(unique(dataset)))), 
               scales = "free_y", 
               space = "free_y") +
    theme(strip.text.y = element_blank(),
          panel.spacing = unit(0, "cm"))
}

# Usage:
# For all data:
#create_token_plot("all")

# For test data:
create_token_plot("test")