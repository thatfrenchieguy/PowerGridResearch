Data37 <- data.frame("Time" = c(1,2,3,4,5,6),"NoTravel" = c(181.5,74.8,39.8,28.1,10.6,10.6),"NominalRoads" = c(181.5,181.5,74.8,49,31.5,10.6), "ConditionalRoads" = c(181.5,74.5,49,31.5,10.6,10.6), "DamagedRoads" = c(181.5,143.2,125.7,125.7,104.8,104.8), "PostProcessed" = c(181.5,74.8,74.8,39.8,28.1,10.6)) 

p = ggplot() + 
  geom_line(data = Data37, aes(x = Time, y = NoTravel, color = "blue")) +
  geom_line(data = Data37, aes(x = Time, y = NominalRoads, color = "red")) +
  geom_line(data = Data37, aes(x = Time, y = ConditionalRoads, color = "green")) +
  geom_line(data = Data37, aes(x = Time, y = DamagedRoads, color = "magenta")) +
  geom_line(data = Data37, aes(x = Time, y = PostProcessed, color = "black")) +
  xlab('Time Steps') +
  ylab('Load Shed')+
  scale_color_discrete(name = "Processing Methods", labels = c("Post Processed", "No Travel", "ConditionalRoads", "DamagedRoads", "NominalRoads"))
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
  scale_color_discrete(name = "Processing Methods", labels = c("Post Processed", "No Travel", "ConditionalRoads", "DamagedRoads", "NominalRoads"))

print(q)

Data302 <- data.frame("Time" = c(1,2,3,4,5,6),"NoTravel" = c(221.7,75.6,49.1,39.6,30.6,27.4),"NominalRoads" = c(221.7,221.7,83.8,60.5,49.1,39.6), "ConditionalRoads" = c(221.7,104.7,83.8,60.5,49.1,39.6), "DamagedRoads" = c(221.7,104.7,83.8,74.8,74.8,74.8), "PostProcessed" = c(221.7,221.7,72.4,49.1,39.6,30.6)) 
r = ggplot() + 
  geom_line(data = Data302, aes(x = Time, y = NoTravel, color = "blue")) +
  geom_line(data = Data302, aes(x = Time, y = NominalRoads, color = "red")) +
  geom_line(data = Data302, aes(x = Time, y = ConditionalRoads, color = "green")) +
  geom_line(data = Data302, aes(x = Time, y = DamagedRoads, color = "magenta")) +
  geom_line(data = Data302, aes(x = Time, y = PostProcessed, color = "black")) +
  xlab('Time Steps') +
  ylab('Load Shed')+
  scale_color_discrete(name = "Processing Methods", labels = c("Post Processed", "No Travel", "ConditionalRoads", "DamagedRoads", "NominalRoads"))

print(r)