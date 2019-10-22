package JavaExtractor.FeaturesEntities;

import java.util.ArrayList;
import java.util.stream.Collectors;

import JavaExtractor.Common.CommandLineValues;
import com.fasterxml.jackson.annotation.JsonIgnore;

public class ProgramFeatures {
	private String name;
	private String originalOperator;
	CommandLineValues m_CommandLineValues;

	private ArrayList<ProgramRelation> features = new ArrayList<>();

	public ProgramFeatures(String name, CommandLineValues m_CommandLineValues) {
		this.name = name;
		this.m_CommandLineValues = m_CommandLineValues;
	}

	@SuppressWarnings("StringBufferReplaceableByString")
	@Override
	public String toString() {
		int lengthOfPadding = m_CommandLineValues.MaxContexts - features.size();
		// Math.max is to avoid making negative sized array later
		lengthOfPadding = Math.max(lengthOfPadding, 0);

		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.append(name);
		stringBuilder.append(originalOperator).append(" ");
		stringBuilder.append(features.stream().map(ProgramRelation::toString).limit(m_CommandLineValues.MaxContexts).collect(Collectors.joining(" ")));

		if (m_CommandLineValues.Padding) {
			String spacePadding = new String(new char[lengthOfPadding]).replace("\0", " ");
			stringBuilder.append(spacePadding);
		}

		return stringBuilder.toString();
	}

	public void addFeature(Property source, String path, Property target) {
		ProgramRelation newRelation = new ProgramRelation(source, target, path);
		features.add(newRelation);
	}

	@JsonIgnore
	public boolean isEmpty() {
		return features.isEmpty();
	}

	public void deleteAllPaths() {
		features.clear();
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getOriginalOperator() {
		return originalOperator;
	}

	public void setOriginalOperator(String originalOperator) {
		this.originalOperator = originalOperator;
	}

	public ArrayList<ProgramRelation> getFeatures() {
		return features;
	}

}
