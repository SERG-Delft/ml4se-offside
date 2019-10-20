package JavaExtractor;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.concurrent.Callable;

import JavaExtractor.Common.*;
import JavaExtractor.Common.Statistics.ContainingNode;
import JavaExtractor.Common.Statistics.OperatorType;
import JavaExtractor.FeaturesEntities.ExtractedMethod;
import com.github.javaparser.ast.body.MethodDeclaration;
import org.apache.commons.lang3.StringUtils;

import com.github.javaparser.ParseException;

import JavaExtractor.FeaturesEntities.ProgramFeatures;

public class ExtractFeaturesTask implements Callable<Void> {
	private static final String GOOD_CODE_NAME = "0";
	private static final String BAD_CODE_NAME = "1";

	CommandLineValues m_CommandLineValues;
	Path filePath;
	MethodExtractor methodExtractor;
	MethodMutator methodMutator;

	public ExtractFeaturesTask(CommandLineValues commandLineValues, Path path) {
		m_CommandLineValues = commandLineValues;
		this.filePath = path;
		this.methodExtractor = new MethodExtractor();
		this.methodMutator = new MethodMutator();
	}

	public ExtractFeaturesTask(CommandLineValues commandLineValues) {
		m_CommandLineValues = commandLineValues;
	}

	@Override
	public Void call() throws Exception {
		//System.err.println("Extracting file: " + filePath);
		processFile();
		//System.err.println("Done with file: " + filePath);
		return null;
	}

	public void processFile() {
		ArrayList<ProgramFeatures> features;
		try {
			if (m_CommandLineValues.Evaluate){
				features = extractSingleFileForEvaluation();
			} else {
				features = extractSingleFileForTraining();
			}

		} catch (ParseException | IOException e) {
			e.printStackTrace();
			return;
		}
		if (features == null) {
			return;
		}

		String toPrint = featuresToString(features);
		// Caller of the JAR should handle writing to a file
		if (toPrint.length() > 0) {
			System.out.println(toPrint);
		}
	}

	public void processCode() {
		String code = m_CommandLineValues.Code;

		ArrayList<ProgramFeatures> features;
		try {
			FeatureExtractor featureExtractor = new FeatureExtractor(m_CommandLineValues);

			features = featureExtractor.extractFeatures(code);

			String toPrint = featuresToString(features);
			if (toPrint.length() > 0) {
				System.out.println(toPrint);
			}
		} catch (ParseException | IOException e) {
			e.printStackTrace();
			return;
		}
	}

	public ArrayList<ProgramFeatures> extractSingleFileForTraining() {
		try {
            FeatureExtractor featureExtractor = new FeatureExtractor(m_CommandLineValues);
			String code = new String(Files.readAllBytes(this.filePath));
			List<MethodDeclaration> methods = methodExtractor.extractMethodsFromCode(code);
			if (methods.size() == 0) return null;

			List<ExtractedMethod> allMethods = new ArrayList<>();
			for (MethodDeclaration method: methods) {
				allMethods.addAll(methodMutator.processMethod(method));
			}
            updateCounters(allMethods);

			ArrayList<ProgramFeatures> allFeatures = new ArrayList<>();

			for (ExtractedMethod extractedMethod: allMethods) {
                ArrayList<ProgramFeatures> features = featureExtractor.extractFeatures(extractedMethod.getMethod().toString());
                features.forEach(feature -> {
                    feature.setName(extractedMethod.getContainingNode());
                    feature.setOriginalOperator(extractedMethod.getOriginalOperator());
                });
                allFeatures.addAll(features);
			}
			return allFeatures;

		} catch (Exception e) {
			e.printStackTrace();
		}

        return null;
	}

	public ArrayList<ProgramFeatures> extractSingleFileForEvaluation() throws IOException, ParseException {
		String code = null;
		try {
			code = new String(Files.readAllBytes(this.filePath));
			List<MethodDeclaration> methods = methodExtractor.extractMethodsFromCode(code);
			FeatureExtractor featureExtractor = new FeatureExtractor(m_CommandLineValues);

			ArrayList<ProgramFeatures> features = featureExtractor.extractFeatures(methodDeclarationsToString(methods));
			features.forEach(programFeatures -> programFeatures.setName(this.filePath.toString() + ":" + programFeatures.getName()));

			return features;
		} catch (IOException e) {
			e.printStackTrace();
			code = Common.EmptyString;
		}

		return new ArrayList<>();
	}

	public String featuresToString(ArrayList<ProgramFeatures> features) {
		if (features == null || features.isEmpty()) {
			return Common.EmptyString;
		}

		List<String> methodsOutputs = new ArrayList<>();

		for (ProgramFeatures singleMethodfeatures : features) {
			StringBuilder builder = new StringBuilder();

			String toPrint = Common.EmptyString;
			toPrint = singleMethodfeatures.toString();
			if (m_CommandLineValues.PrettyPrint) {
				toPrint = toPrint.replace(" ", "\n\t");
			}
			builder.append(toPrint);


			methodsOutputs.add(builder.toString());

		}
		return StringUtils.join(methodsOutputs, "\n");
	}

	private String methodDeclarationsToString(List<MethodDeclaration> methodDeclarations) {
		StringWriter stringWriter = new StringWriter();
		PrintWriter writer = new PrintWriter(stringWriter, true);
		for (MethodDeclaration declaration : methodDeclarations) {
			writer.println(declaration);
		}
		return stringWriter.toString();
	}

	private void updateCounters(List<ExtractedMethod> allMethods) {
        for (OperatorType.Type operatorType: OperatorType.Type.values()) {
        	long count = allMethods.stream()
					.filter(em -> em.getOriginalOperator().equals(operatorType.name()))
					.count();
        	if (count > 0) App.incrementOperatorType(operatorType.name(), count);
        }
        for (ContainingNode containingNode: ContainingNode.values()) {
        	long count = allMethods.stream()
					.filter(em -> em.getContainingNode().equals(containingNode.toString()))
					.count();
        	if (count > 0) App.incrementInputCategory(containingNode.toString(), count);
        }

		long count = allMethods.stream()
				.filter(em -> em.getContainingNode().equals(App.noBugString))
				.count();
		if (count > 0) App.incrementInputCategory(App.noBugString, count);

    }
}
