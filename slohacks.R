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

cleaner_data <- anomaly_data %>% 
  filter(DELIVERED_QUANTITY>0&DC_QTY>0)%>%
  mutate(unit_price_discrepancy = abs((DELIVERED_PRICE/DELIVERED_QUANTITY)-UNIT_PRICE))

tsd <- cleaner_data %>%
  filter(unit_price_discrepancy<=1&DC_QTY==DELIVERED_QUANTITY)%>%
  mutate(month = month(TRANSACTION_DATE)) %>%
  filter(ACCOUNT_NAME=="BRINKER-CHILI'S #075")%>%
  filter(ORGANIZATION.NUMBER=="FRESHPOINT_158")%>%
  filter(CENTER_PROD_NUM  == 101217)

#not just delivered price, but also other numerical variables
tsd <- data.frame(tsd$TRANSACTION_DATE,tsd$DELIVERED_PRICE)
tsd_tbl_time <- as_tbl_time(tsd, tsd.TRANSACTION_DATE)

dataGraph <- tsd_tbl_time%>%
  time_decompose(tsd.DELIVERED_PRICE, method = "STL",frequency = "auto",trend = "auto") %>%
  anomalize(remainder, method = "iqr",alpha = 0.025) %>%
  time_recompose() %>%
  # Anomaly Visualization
  plot_anomalies(time_recomposed = TRUE, ncol = 3, alpha_dots = 0.25, color_no = "#0c5e2b", color_yes = "#e86e22", fill_ribbon = "#a4c1ad") +
  labs(title = "ITRADE Anomaly Detection", subtitle = "ACCOUNT, ORGANIZATION, DCPRODUCTNAME", x= "Transaction Date", 
       y = "Delivered Price")

ui <- fluidPage(theme = shinytheme("flatly"),
  sidebarPanel (
    selectInput("ACCOUNT_NAME", label= "Account", choices = as.vector(unique(anomaly_data$ACCOUNT_NAME)))
  ),
  mainPanel (
    plotOutput("plot")
  )
)

server <- function(input, output) {
  output$plot <- renderPlot({
    dataGraph
  })
  
  output$histogram <- renderPlot({
    #ggplot(...)
  })
}

shinyApp(ui = ui, server = server)