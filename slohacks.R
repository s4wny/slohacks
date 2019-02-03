library(ggplot2)
library(tidyverse)
library(shiny)
library(shinythemes)
library(anomalize)
library(tidyverse)
library(tibbletime)
library(lubridate)

anomaly_data <- read.csv("Anomaly_Data.csv")
anomaly_data$DC_QTY <- as.numeric(as.character(anomaly_data$DC_QTY))
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "MAR",replacement="03")
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "APR",replacement="04")
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "MAY",replacement="05")
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "JUN",replacement="06")
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "JUL",replacement="07")
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "AUG",replacement="08")
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "SEP",replacement="09")
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "OCT",replacement="10")
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "NOV",replacement="11")
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "DEC",replacement="12")
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "JAN",replacement="01")
anomaly_data$TRANSACTION_DATE = str_replace_all(anomaly_data$TRANSACTION_DATE,pattern = "FEB",replacement="02")
anomaly_data$TRANSACTION_DATE = dmy(anomaly_data$TRANSACTION_DATE)

newdata <- data.frame(anomaly_data$TRANSACTION_DATE,anomaly_data$DELIVERED_PRICE)
ex1_tbl_time <- as_tbl_time(newdata, anomaly_data.TRANSACTION_DATE)

dataGraph <- ex1_tbl_time%>%
  as_period("daily")%>%
  time_decompose(anomaly_data.DELIVERED_PRICE, method = "stl") %>%
  anomalize(remainder, method = "iqr") %>%
  time_recompose() %>%
  # Anomaly Visualization
  plot_anomalies(time_recomposed = TRUE, ncol = 3, alpha_dots = 0.25) +
  labs(title = "Tidyverse Anomalies", subtitle = "STL + IQR Methods")

ui <- fluidPage(theme = shinytheme("flatly"),
  mainPanel (
    plotOutput("plot")
  )
)

server <- function(input, output) {
  output$plot <- renderPlot({
    dataGraph
  })
}

shinyApp(ui = ui, server = server)