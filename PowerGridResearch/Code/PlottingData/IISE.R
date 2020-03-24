library(ggplot2)
Data37 <- data.frame("Time" = c(1,2,3,4,5,6),"NoTravel" = c(187.5,48.8,10.6,0,0,0),"NominalRoads" = c(187.7,187.7,69.9,28.1,6,0), "ConditionalRoads" = c(187.7,69.9,28.1,6,0,0), "PostProcessed" = c(187.7,74.8,36.4,36.4,32.5,0)) 

p = ggplot() + 
  geom_line(data = Data37, aes(x = Time, y = NoTravel, color = "blue")) +
  geom_line(data = Data37, aes(x = Time, y = NominalRoads, color = "red")) +
  geom_line(data = Data37, aes(x = Time, y = ConditionalRoads, color = "green")) +
  geom_line(data = Data37, aes(x = Time, y = PostProcessed, color = "black")) +
  xlab('Time Steps') +
  ylab('Load Shed')+
  scale_color_discrete(name = "Processing Methods", labels = c("Post Processed", "No Travel Time", "Roads First Iterated", "Nominal Condition Roads w/delay"))
 print(p)

Data57<- data.frame("Time" = c(1,2,3,4,5,6),"NoTravel" = c(517.1,133.3,87.3,65.3,65.3,38.8),"NominalRoads" = c(517.1,517.1,133.3,111.4,87.3,65.3), "ConditionalRoads" = c(517.1,140.1,118.1,96.2,65.3,65.3), "DamagedRoads" = c(517.1,140.1,118.2,96.2,87.3,65.3), "PostProcessed" = c(517.1,140.1,133.3,87.3,65.3,65.3)) 

q = ggplot() + 
  geom_line(data = Data57, aes(x = Time, y = NoTravel, color = "blue")) +
  geom_line(data = Data57, aes(x = Time, y = NominalRoads, color = "red")) +
  geom_line(data = Data57, aes(x = Time, y = ConditionalRoads, color = "green")) +
  geom_line(data = Data57, aes(x = Time, y = DamagedRoads, color = "magenta")) +
  geom_line(data = Data57, aes(x = Time, y = PostProcessed, color = "black")) +
  xlab('Time Steps') +
  ylab('Load Shed')+
  scale_color_discrete(name = "Processing Methods", labels = c("Post Processed", "No Travel Time", "Roads First Iterated", "Statically Damaged Roads", "Nominal Condition Roads w/delay"))

print(q)

Data30Rand <- data.frame("Time" = c(1,2,3,4,5,6),"NoTravel" = c(219.7,38.2,13,3.5,0,0),"NominalRoads" = c(219.7,219.7,68.2,29.5,7,0), "ConditionalRoads" = c(219.7,70.4,40.4,15.2,3.5,0), "DamagedRoads" = c(219.7,70.4,40.4,25.2,16.5,0), "PostProcessed" = c(219.7,132.4,28.2,13,3.5,0)) 
r = ggplot() + 
  geom_line(data = Data30Rand, aes(x = Time, y = NoTravel, color = "blue")) +
  geom_line(data = Data30Rand, aes(x = Time, y = NominalRoads, color = "red")) +
  geom_line(data = Data30Rand, aes(x = Time, y = ConditionalRoads, color = "green")) +
  geom_line(data = Data30Rand, aes(x = Time, y = DamagedRoads, color = "magenta")) +
  geom_line(data = Data30Rand, aes(x = Time, y = PostProcessed, color = "black")) +
  xlab('Time Steps') +
  ylab('Load Shed')+
  scale_color_discrete(name = "Processing Methods", labels = c("Post Processed", "No Travel Time", "Roads First Iterated", "Statically Damaged Roads", "Nominal Condition Roads w/delay"))

print(r)
