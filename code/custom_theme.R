library(showtext)
font_add_google("Roboto Condensed", "robotoc")
font_add_google("Roboto Slab", "robotos")
font_add_google("Overpass", "overpass")
showtext_auto()

act_theme = theme_minimal(base_family = "overpass",
                          base_size = 9) +
    theme(
        legend.pos = "bottom",
        legend.direction = "horizontal",
        legend.title = element_blank(),
        legend.text = element_markdown(
            size = 11
        ),
        plot.background = element_rect(fill = "#F5F4EF", color = NA),
        plot.margin = margin(20, 30, 20, 30),
        plot.title = element_markdown(
            margin = margin(0, 0, 20, 0), 
            size = 26, 
            family = "robotos", 
            face = "bold", 
            vjust = 0, 
            color = "grey25"
        ),
        plot.caption = element_textbox_simple(size = 7,
                                              color = "grey20"),
        axis.title = element_blank(),
        axis.text = element_text(color = "grey40"),
        strip.text = element_text(face = "bold",
                                  color = "grey50"),
        plot.subtitle = element_textbox_simple(
            size = 11,
            lineheight = 1,
            margin = margin(-15, 0, 10, 0),
        )
    )
ggplot2::theme_set(act_theme)
